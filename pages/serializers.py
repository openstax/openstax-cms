from rest_framework import serializers

from pages.models import GeneralPage


class GeneralPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralPage
        fields = ('id', 'title', 'slug', 'body')
