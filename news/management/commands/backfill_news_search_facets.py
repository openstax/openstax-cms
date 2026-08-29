"""
Backfill NewsArticleSubject/NewsArticleCollection/NewsArticleContentType from
each NewsArticle's article_subjects/collections/content_types StreamFields —
for rows saved before NewsArticle.save() started keeping them in sync, or
touched since via a bare .update() (which bypasses save()).

DRY RUN BY DEFAULT — pass --commit to write.

Idempotent: NewsArticle._sync_search_facets() deletes and recreates each
article's three link sets from its current StreamField values every time, so
re-running always converges on the same end state.
"""
from django.core.management.base import BaseCommand

from news.models import NewsArticle, _facet_ids


class Command(BaseCommand):
    help = (
        "Backfill NewsArticleSubject/NewsArticleCollection/NewsArticleContentType "
        "from each NewsArticle's StreamFields. DRY RUN BY DEFAULT — pass --commit to write."
    )

    def add_arguments(self, parser):
        parser.add_argument('--commit', action='store_true',
                             help="Write changes. Without this, runs in dry-run mode.")

    def handle(self, *args, **options):
        commit = options['commit']
        if not commit:
            self.stdout.write(self.style.WARNING(
                "*** DRY RUN — no changes will be written. Pass --commit to save. ***"))

        count = subject_links = collection_links = content_type_links = 0

        for article in NewsArticle.objects.all().iterator():
            count += 1
            subject_links += len(_facet_ids(article.article_subjects, 'subject'))
            collection_links += len(_facet_ids(article.collections, 'collection'))
            content_type_links += len(_facet_ids(article.content_types, 'content_type'))
            if commit:
                article._sync_search_facets()

        self.stdout.write(
            f"{'Synced' if commit else 'Would sync'} {count} article(s): "
            f"{subject_links} subject link(s), {collection_links} collection link(s), "
            f"{content_type_links} content type link(s).")
        if not commit:
            self.stdout.write(self.style.WARNING(
                "*** DRY RUN — no changes were written. Pass --commit to save. ***"))
