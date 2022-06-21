from webinars.models import webinar_subject_search
from django.http import JsonResponse


def search(request):
    found_entries = []
    if ('subjects' in request.GET) and request.GET['subjects'].strip():
        subject = request.GET['subjects']
        found_entries = webinar_subject_search(subject)

    search_results_json = []
    search_results_shown = set()
    for result in found_entries:
        if result.title in search_results_shown:
            continue

        search_results_shown.add(result.title)
        search_results_json.append({
            'id': result.id,
            'title': result.title,
            'start': result.start,
            'end': result.end,
            'description': result.description,
            'speakers': result.speakers,
            'spaces_remaining': result.spaces_remaining,
            'registration_url': result.registration_url,
            'registration_link_text': result.registration_link_text,
            'display_on_tutor_page': result.display_on_tutor_page,
            'selected_subjects': result.selected_subjects,
        })
    return JsonResponse(search_results_json, safe=False)