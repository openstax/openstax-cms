from pgvector.django import VectorField

from django_ai_core.contrib.index.storage.pgvector.models import BasePgVectorEmbedding


class PageEmbedding(BasePgVectorEmbedding):
    # 1536 = OpenAI text-embedding-3-small dimensions.
    vector = VectorField(dimensions=1536)
