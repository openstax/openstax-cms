from django.apps import AppConfig


class SearchConfig(AppConfig):
    name = 'search'

    def ready(self):
        # Deferred: these import each app's models, which isn't safe to touch
        # until the app registry has finished loading every app.
        from news.search import build_news_queryset, serialize_article
        from books.search import build_book_queryset, serialize_book
        from webinars.search_v2 import build_webinar_queryset, serialize_webinar
        from .registry import SearchSource, register

        register(SearchSource(key='news', build_results=build_news_queryset, to_dict=serialize_article))
        register(SearchSource(key='books', build_results=build_book_queryset, to_dict=serialize_book))
        register(SearchSource(key='webinars', build_results=build_webinar_queryset, to_dict=serialize_webinar))
