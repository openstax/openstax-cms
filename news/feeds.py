from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import NewsArticle

class LatestEntriesFeed(Feed):
    title = "OpenStax Blog Feed"
    link = "/blog-feed/"
    description = "Updates and changes in the world of OpenStax"

    def items(self):
        return NewsArticle.objects.order_by('date')[:5]

    def item_heading(self, item):
        return item.heading

    def item_description(self, item):
        return item.body

    def item_guid(self, item):
        return str(item.pk)

    def item_link(self, item):
        return '/blog/{}'.format(item.slug)