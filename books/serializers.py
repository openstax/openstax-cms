from .models import BookIndex, Book

from rest_framework import serializers


from wagtail.contrib.wagtailapi.serializers import PageSerializer


class BookIndexSerializer(PageSerializer):
    books = serializers.ModelJSONField()

    class Meta:
        model = BookIndex
        fields = BookIndex.api_fields


class BookSerializer(PageSerializer):
    class Meta:
        model = Book
        fields = Book.api_fields
