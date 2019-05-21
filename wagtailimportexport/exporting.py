import json, os, argparse
from zipfile import ZipFile
from tempfile import TemporaryDirectory

import wagtail

from django.core.files import File
from django.core.files.storage import get_storage_class
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.base import ModelState
from django.db.models.fields.files import FieldFile
from wagtail.core.blocks import StreamValue
from wagtail.images import get_image_model
from wagtail.snippets.models import SNIPPET_MODELS
from wagtailimportexport.compat import Page

from wagtail.images.models import Image

from django.conf import settings



def export_pages(root_page=None, export_unpublished=False, null_users=False, null_images=True):
    """
    Create a JSON-able dict definition of part of a site's page tree 
    starting from root_page and descending into its descendants

    By default only published pages are exported.

    If a page is unpublished it and all its descendants are pruned even
    if some of those descendants are themselves published. This ensures
    that there are no orphan pages when the subtree is created in the
    destination site.

    If export_unpublished=True the root_page and all its descendants
    are included.
    """
    if root_page is None:
        root_page = Page.objects.filter(url_path='/').first()
    pages = Page.objects.descendant_of(
        root_page, inclusive=True).order_by('path').specific()
    if not export_unpublished:
        pages = pages.filter(live=True)

    page_data = []
    exported_paths = set()
    for (i, page) in enumerate(pages):
        parent_path = page.path[:-(Page.steplen)]
        # skip over pages whose parents haven't already been exported
        # (which means that export_unpublished is false and the parent was unpublished)
        if i == 0 or (parent_path in exported_paths):

            # Turn page data to a dictionary.
            data = json.loads(page.to_json())

            # Get the list of field names where images are used.
            images = list_images(page._meta.get_fields())

            # Turning images into a dictionary and storing the image id.
            images = {key : data[key] for key in images}

            # Updating images dictionary and assigning the data of the instance
            # if the img_id is valid.
            for (field, img_id) in images.items():
                if img_id: 
                    images[field] = instance_to_data(Image.objects.get(pk=img_id), null_users=null_users)

            # Null the owner of the page.
            if null_users == True and data.get('owner') is not None:
                data['owner'] = None

            # Null all the images.
            if null_images == True:
                for image in images:
                    if data.get(image) is not None:
                        data[image] = None

            # Export page data.
            page_data.append({
                'content': data,
                'model': page.content_type.model,
                'app_label': page.content_type.app_label,
                'images': images
            })

            exported_paths.add(page.path)
    return page_data


def export_snippets():
    """
    Create and return a JSON-able dict of the instance's snippets
    """
    snippet_data = {}
    for Model in SNIPPET_MODELS:
        module_name = Model.__module__.split('.')[0]
        model_key = '.'.join([module_name, Model.__name__])  # for django.apps.apps.get_model(...)
        snippets = Model.objects.all()
        snippet_data[model_key] = [instance_to_data(snippet) for snippet in snippets]
    return snippet_data


def list_images(fields):
    """
    Returns the list of all fields that has the related_model of models.Image
    """
    images = []
    for field in fields:
        if field.related_model and str(field.related_model) == "<class 'wagtail.images.models.Image'>":
            images.append(field.name)
    return images

def instance_to_data(instance, null_users=False):
    """A utility to create JSON-able data from a model instance"""
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


def zip_content(content_data):
    """
    Create and return a ZIP file containing the instance's content data and images
    """
    file_storage = get_storage_class()()
    with TemporaryDirectory() as tempdir:
        zfname = os.path.join(tempdir, 'content.zip')
        with ZipFile(zfname, 'w') as zf:
            zf.writestr(
                'content.json',
                json.dumps(content_data, indent=2, cls=DjangoJSONEncoder))
            for page in content_data['pages']:
                for image_def in page['images'].values():
                    if image_def:
                        print(image_def)
                        filename = image_def['file']['name']
                        with file_storage.open(filename, 'rb') as f:
                            zf.writestr(filename, f.read())
        with open(zfname, 'rb') as zf:
            fd = zf.read()
    return fd
