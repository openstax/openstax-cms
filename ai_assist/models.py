from django.db import models

from pgvector.django import CosineDistance, VectorField


class PageEmbeddingQuerySet(models.QuerySet):
    def annotate_with_distance(self, query_vector):
        return self.annotate(distance=CosineDistance("vector", query_vector))


class PageEmbeddingManager(models.Manager.from_queryset(PageEmbeddingQuerySet)):
    pass


class PageEmbedding(models.Model):
    # Standalone pgvector storage for PageVectorIndex. Not subclassing
    # django_ai_core's BasePgVectorEmbedding on purpose: importing that module
    # also registers its concrete PgVectorEmbedding model (no migration shipped),
    # which breaks `makemigrations --check`.
    index_name = models.CharField(max_length=255)
    document_key = models.CharField(max_length=255, primary_key=True)
    content = models.TextField()
    metadata = models.JSONField(default=dict)
    vector = VectorField(dimensions=1536)

    objects = PageEmbeddingManager()

    def __str__(self):
        return self.document_key
