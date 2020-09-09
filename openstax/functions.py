from django.conf import settings
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

    if "book_faculty_resources" in response.data:
        for res_id in range(len(response.data["book_faculty_resources"])):
            if not response.data["book_faculty_resources"][res_id]["resource_unlocked"]:
                response.data["book_faculty_resources"][res_id]["link_document_url"] = ""
                response.data["book_faculty_resources"][res_id]["link_external"] = ""
                any_hidden = True
                
    return any_hidden

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