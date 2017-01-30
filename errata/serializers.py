from .models import Errata
from books.models import Book

from rest_framework import serializers


class ErrataSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())
    error_type = serializers.StringRelatedField()
    resource = serializers.StringRelatedField(many=True)

    class Meta:
        model = Errata
        fields = '__all__'
