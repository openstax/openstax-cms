from .models import NewsIndex, NewsArticle

from wagtail.contrib.wagtailapi.serializers import PageSerializer


class NewsIndexSerializer(PageSerializer):
    class Meta:
        model = NewsIndex
        fields = NewsIndex.api_fields


class NewsArticleSerializer(PageSerializer):
    class Meta:
        model = NewsArticle
        fields = NewsArticle.api_fields
