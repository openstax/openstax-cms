import html2text
from django.contrib.syndication.views import Feed
from .models import NewsArticle
from django.utils.feedgenerator import Atom1Feed


class RssBlogFeed(Feed):
    title = "OpenStax Blog Feed"
    link = "/blog-feed/"
    description = "Updates and changes in the world of OpenStax"

    def items(self):
        return NewsArticle.objects.order_by('-date')

    def item_heading(self, item):
        return item.heading

    def item_description(self, item):
        h = html2text.HTML2Text()
        excerpt = h.handle(str(item.body)).split('\n\n')[0]
        return excerpt + "..."

    def item_guid(self, item):
        return str(item.pk)

    def item_link(self, item):
        return '/blog/{}'.format(item.slug)


class AtomBlogFeed(RssBlogFeed):
    feed_type = Atom1Feed
    subtitle = RssBlogFeed.description
