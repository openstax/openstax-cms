from django.conf import settings
from django.http import JsonResponse
from wagtail.core.models import Site


def build_document_url(url):
    if url:
        site = Site.objects.get(is_default_site=True)
        if site.port == 80 or site.port == 443:
            folder = url.split('/')[1]
            filename = url.split('/')[-1]
            return "{}{}/{}".format(settings.MEDIA_URL, folder, filename)
        else:
            return "http://{}:{}{}".format(site.hostname, site.port, url)
    else:
        return None


def build_image_url(image):
    if image:
        site = Site.objects.get(is_default_site=True)
        if site.port == 80 or site.port == 443:
            return "{}{}".format(settings.MEDIA_URL, image.file)
        else:
            return "http://{}:{}/api/v0/images/{}".format(site.hostname, site.port, image.pk)
    else:
        return None

def remove_locked_links_detail(response):
    """
    Checks whether the response has a key 'book_faculty_resources',
    and if so, removes the 'link_document_url' and 'link_external' if 'resource_unlocked'
    is set to True.

    Returns True if at least a link is hidden.
    """

    any_hidden = False
    print('response: ' + str(response.data.book_faculty_resources.values()[0]))
    faculty_resources = []
    video_resources = []
    orientation_resources = []
    for faculty_resource in response.data.book_faculty_resources.values():

        #print(FacultyResources.objects.filter(id=faculty_resource['link_document_id']).values())
        faculty_resources.append(faculty_resource)

    faculty_resource_json = {}
    faculty_resource_json['book_faculty_resources'] = faculty_resources
    faculty_resource_json['book_video_faculty_resources'] = video_resources
    faculty_resource_json['book_orientation_faculty_resources'] = faculty_resources
    #faculty_resource_json.append({response.data.book_faculty_resources.values()})
    #faculty_resource_json.append({response.data.book_video_faculty_resources.values()})
    #faculty_resource_json.append({response.data.book_orientation_faculty_resources.values()})

    # if response.data.book_faculty_resources:
    #     for resource in response.data.book_faculty_resources:
    #         if not resource["resource_unlocked"]:
    #             resource["link_document_url"] = ""
    #             resource["link_external"] = ""
    #             any_hidden = True
                
    return JsonResponse(faculty_resource_json, safe=False)

def remove_locked_links_listing(response):
    """
    Checks whether the any response in all responses has a key 'book_faculty_resources',
    and if so, removes the 'link_document_url' and 'link_external' if 'resource_unlocked'
    is set to True.

    Returns True if at least a link is hidden.
    """

    any_hidden = False

    for item_id, item in enumerate(response.data["items"]):
        if "book_faculty_resources" in item:
            for res_id in range(len(item["book_faculty_resources"])):
                if not item["book_faculty_resources"][res_id]["resource_unlocked"]:
                    response.data["items"][item_id]["book_faculty_resources"][res_id]["link_document_url"] = ""
                    response.data["items"][item_id]["book_faculty_resources"][res_id]["link_external"] = ""
                    any_hidden = True

    return any_hidden

