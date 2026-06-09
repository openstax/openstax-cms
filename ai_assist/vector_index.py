from django_ai_core.contrib.index import (
    CachedEmbeddingTransformer,
    CoreEmbeddingTransformer,
    ModelSource,
    VectorIndex,
    registry,
)
from django_ai_core.contrib.index.embedding import EmbeddingTransformer
from django_ai_core.contrib.index.storage.pgvector.provider import PgVectorProvider

from wagtail_ai.agents.base import get_llm_service

CONTENT_FIELDS = ["title", "search_description"]


class LazyEmbeddingTransformer(EmbeddingTransformer):
    """Defers LLM-service creation until first use, so app startup and CI don't
    require an embedding API key (any-llm validates the key at client creation)."""

    def __init__(self, alias="embedding"):
        self.alias = alias
        self._inner = None

    def _resolve(self):
        if self._inner is None:
            self._inner = CachedEmbeddingTransformer(
                CoreEmbeddingTransformer(get_llm_service(self.alias))
            )
        return self._inner

    @property
    def transformer_id(self):
        return f"lazy_{self.alias}"

    def embed_string(self, text):
        return self._resolve().embed_string(text)

    def embed_documents(self, documents, **kwargs):
        return self._resolve().embed_documents(documents, **kwargs)


def _sources():
    from books.models import Book
    from news.models import NewsArticle
    from pages.models import FlexPage

    return [
        ModelSource(model=NewsArticle, content_fields=CONTENT_FIELDS),
        ModelSource(model=Book, content_fields=CONTENT_FIELDS),
        ModelSource(model=FlexPage, content_fields=CONTENT_FIELDS),
    ]


def register_page_index():
    from ai_assist.models import PageEmbedding

    @registry.register()
    class PageVectorIndex(VectorIndex):
        sources = _sources()
        embedding_transformer = LazyEmbeddingTransformer()
        storage_provider = PgVectorProvider(model=PageEmbedding)

    return PageVectorIndex
