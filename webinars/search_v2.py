from wagtail.search.backends import get_search_backend

from .models import Webinar


def build_webinar_queryset(get_params):
    """New pair for the search registry. webinars/search.py (hand-rolled
    SearchVector, its own rank threshold, no pagination) stays untouched -
    the webinars page still calls that route directly.

    Webinar isn't a Page, so its default manager has no .search() of its
    own; call the backend directly instead (it accepts a plain queryset).
    """
    q = get_params.get('q', '').strip()
    qs = Webinar.objects.all()
    if q:
        return get_search_backend().search(q, qs)
    return qs.order_by('-start')


def serialize_webinar(webinar):
    return {
        'id': webinar.id,
        'title': webinar.title,
        'description': webinar.description,
        'start': webinar.start,
        'end': webinar.end,
        'speakers': webinar.speakers,
        'spaces_remaining': webinar.spaces_remaining,
        'registration_url': webinar.registration_url,
        'registration_link_text': webinar.registration_link_text,
        'display_on_tutor_page': webinar.display_on_tutor_page,
        'subjects': webinar.selected_subjects,
        'collections': webinar.selected_collections,
    }
