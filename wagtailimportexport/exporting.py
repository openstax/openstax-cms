import io
import json
import logging
import copy

from django.core.files import File
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.base import ModelState
from django.db.models.fields.files import FieldFile

from wagtail.models import Page
from wagtail.blocks import StreamValue
from wagtail.images.models import Image

from wagtailimportexport import functions
from wagtailimportexport.config import app_settings
from wagtail.documents.models import Document


def export_page(settings={'root_page': None, 'export_unpublished': False,
                          'export_documents': False, 'export_images': False, 'null_pk': True,
                          'null_fk': False, 'null_users': False
                          }):
    """
    Exports the root_page as well as its children (if the setting is set).

    Arguments:
    settings -- A dictionary that holds settings from cleared form data.

    Returns:
    A zip archive of the exported pages; if it fails at any point, returns
    None and logs the error.
    """

    settings = copy.deepcopy(settings)

    # If root_page is not set, then set it the main directory as default.
    if not settings['root_page']:
        settings['root_page'] = Page.objects.filter(url_path='/').first()

    # Get the list of the pages, (that are the descendant of the root_page).
    pages = Page.objects.descendant_of(
        settings['root_page'], inclusive=True).order_by('path').specific()

    # Filter the pages if export_unpublished is set to false.
    if not settings['export_unpublished']:
        pages = pages.filter(live=True)

    # Initialize the variables.
    page_data = []
    exported_paths = set()

    # Start looping through pages and export their content.
    for (i, page) in enumerate(pages):
        parent_path = page.path[:-(Page.steplen)]

        # skip over pages whose parents haven't already been exported
        # (which means that export_unpublished is false and the parent was unpublished)
        if i == 0 or (parent_path in exported_paths):

            # Turn page data to a dictionary.
            data = json.loads(page.to_json())
            locale = data['locale']

            # look up document titles
            if page.content_type.model == 'book':
                cover = functions.document_title(data['cover'])
                title_image = functions.document_title(data['title_image'])
                hi_res_pdf = functions.document_title(data['high_resolution_pdf'])
                lo_res_pdf = functions.document_title(data['low_resolution_pdf'])
                community_logo = functions.document_title(data['community_resource_logo'])
                community_feature_link = functions.document_title(data['community_resource_feature_link'])

            # Get list (and metadata) of images and documents to be exported.
            images = list_fileobjects(page, settings, Image) if settings['export_images'] else {}
            documents = list_fileobjects(page, settings, Document) if settings['export_documents'] else {}

            # Remove FKs
            if settings['null_fk']:
                functions.null_fks(page, data)

            #Remove the owner of the page.
            if settings['null_users'] and not data.get('owner'):
                data['owner'] = None

            # Null all the images.
            if settings['export_images']:
                for image in images:
                    if data.get(image) is not None:
                        data[image] = None

            data['pk'] = None
            data['locale'] = locale
            # add document titles to data
            if page.content_type.model == 'book':
                data['cover'] = cover
                data['title_image'] = title_image
                data['high_resolution_pdf'] = hi_res_pdf
                data['low_resolution_pdf'] = lo_res_pdf
                data['community_resource_logo'] = community_logo
                data['community_resource_feature_link'] = community_feature_link

            # Export page data.
            page_data.append({
                'content': data,
                'model': page.content_type.model,
                'app_label': page.content_type.app_label,
                'images': images,
                'documents': documents
            })

            exported_paths.add(page.path)

    return functions.zip_contents(page_data)


def list_fileobjects(page, settings, objtype):
    """
    Returns a dict of all fields that has the related_model of objtype as well as their metadata.

    Arguments:
    page -- Page instance with supported fields.
    settings -- Settings dictionary from main method.
    objtype -- Image, Document from Wagtail.

    Returns:
    A dictionary of fields with their respective metadata.
    """

    data = json.loads(page.to_json())

    if objtype == Image:
        related_model_by = "<class 'wagtail.images.models.Image'>"
    elif objtype == Document:
        related_model_by = "<class 'wagtail.documents.models.Document'>"
    else:
        return {}

    objects = {}
    for field in page._meta.get_fields():
        if field.related_model and str(field.related_model) == related_model_by:
            if data[field.name]:

                try:
                    # Get the object instance.
                    instance = objtype.objects.get(pk=data[field.name])

                    # Null the object if the filesize is larger.
                    if instance.file.size > app_settings['max_file_size'] and settings['ignore_large_files']:
                        objects[field.name] = None
                    else:
                        objects[field.name] = instance_to_data(instance, null_users=settings['null_users'])

                except (FileNotFoundError, objtype.DoesNotExist):
                    logging.error("File for " + str(field.name) + " is not found on the environment, skipping.")
                    objects[field.name] = None

            else:
                objects[field.name] = None

    return objects


def instance_to_data(instance, null_users=False):
    """
    A utility to create JSON-able data from a model instance.

    Arguments:
    instance -- objects.get() object instance.
    null_users -- Whether to null user references.

    Returns:
    A dictionary of metadata of instance.
    """

    data = {}

    for key, value in instance.__dict__.items():
        if isinstance(value, ModelState):
            continue
        elif null_users == True and ('user_id' in key or 'owner' in key):
            data[key] = None
        elif isinstance(value, StreamValue):
            data[key] = json.dumps(value.stream_data, cls=DjangoJSONEncoder)
        elif isinstance(value, FieldFile) or isinstance(value, File):
            data[key] = {'name': value.name, 'size': value.size}
        else:
            data[key] = value
    return data