import io
import json
import logging
import traceback
from zipfile import ZipFile

from django.apps import apps
from django.core.files.images import ImageFile
from django.core.files.base import File
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction, IntegrityError

from modelcluster.models import get_all_child_relations

from wagtail.models import Page
from wagtail.images.models import Image

from wagtailimportexport import functions
import snippets.models as snippets


def import_page(uploaded_archive, parent_page, overwrites={}):
    """
    Imports uploaded_archive as children of parent_page.

    Arguments:
    uploaded_archive -- A file object, which includes contents.json
    and the media objects.
    parent_page -- Page object, where the page(s) will be imported to.

    Returns:
    numpages -- Integer value of number of pages that were successfully
    imported.
    numfails -- Integer value of number of pages that were failed to be
    imported.
    message -- String message to report any warning/issue.
    """

    # Read the zip archive and load as 'payload'.
    payload = io.BytesIO(uploaded_archive.read())

    # Open zip archive.
    with ZipFile(payload, 'r') as zf:
        try:
            # Open content.json and load them into contents dictionary.
            with zf.open('content.json') as mf:
                contents = json.loads(mf.read().decode('utf-8-sig'))
                error_msg = ''

                # First create the base Page records; these contain no foreign keys, so this allows us to
                # build a complete mapping from old IDs to new IDs before we go on to importing the
                # specific page models, which may require us to rewrite page IDs within foreign keys / rich
                # text / streamfields.
                page_content_type = ContentType.objects.get_for_model(Page)

                # Unzip all the files in the zip directory.
                contents_mapping = functions.unzip_contents(zf)

                # Get the list of pages to skip.
                existing_pages = list_existing_pages(contents) if not overwrites else []

                # Dictionaries to store original paths.
                pages_by_original_path = {}
                pages_by_original_id = {}

                # Loop through all the pages.
                for (i, page_record) in enumerate(contents):

                    new_field_datas = {}
                    content_type = functions.content_type_by_model(page_record['model'])
                    #content_type = page_record['content']['content_type']

                    # Skip the existing pages.
                    if i in existing_pages:
                        error_msg = 'Import stopped. Duplicate slug: ' + str(page_record['content']['slug'])
                        continue

                    # Reassign image IDs.
                    for (fieldname, filedata) in page_record["images"].items():

                        new_field_datas[fieldname] = None

                        # Skip if the image is set to null.
                        if not filedata:
                            continue

                        local_file_query = get_fileobject(filedata["file"]["name"].split("/")[-1], Image)

                        local_file_id = local_file_query if local_file_query else create_fileobject(
                            filedata["title"], contents_mapping[filedata["file"]["name"]], Image)

                        new_field_datas[fieldname] = local_file_id

                    # Overwrite image and document IDs
                    for (field, new_value) in new_field_datas.items():
                        page_record['content'][field] = new_value

                    # Misc. overwrites
                    for (field, new_value) in overwrites.items():
                        page_record['content'][field] = new_value

                    if page_record['model'] == 'book':
                        # look up document ids
                        page_record['content']['cover'] = functions.document_id(page_record['content']['cover'])
                        page_record['content']['title_image'] = functions.document_id(page_record['content']['title_image'])
                        page_record['content']['high_resolution_pdf'] = functions.document_id(page_record['content']['high_resolution_pdf'])
                        page_record['content']['low_resolution_pdf'] = functions.document_id(page_record['content']['low_resolution_pdf'])
                        page_record['content']['community_resource_logo'] = functions.document_id(page_record['content']['community_resource_logo'])
                        page_record['content']['community_resource_feature_link'] = functions.document_id(page_record['content']['community_resource_feature_link'])

                    # set page.pk to null if pk already exists
                    pages = Page.objects.all()
                    for p in pages:
                        if p.pk == page_record['content']['pk']:
                            page_record['content']['pk'] = None
                            break

                    page_record['content']['content_type'] = content_type
                    # Create page instance.
                    page = Page.from_serializable_data(page_record['content'])

                    original_path = page.path
                    original_id = page.id

                    # Clear id and treebeard-related fields so that they get reassigned when we save via add_child
                    page.id = None
                    page.path = None
                    page.depth = None
                    page.numchild = 0
                    page.url_path = None
                    page.content_type = page_content_type

                    # Handle children of the imported page(s).
                    if i == 0:
                        parent_page.add_child(instance=page)
                    else:
                        # Child pages are created in the same sibling path order as the
                        # source tree because the export is ordered by path
                        parent_path = original_path[:-(Page.steplen)]
                        pages_by_original_path[parent_path].add_child(instance=page)

                    pages_by_original_path[original_path] = page
                    pages_by_original_id[original_id] = page

                    # Get the page model of the source page by app_label and model name
                    # The content type ID of the source page is not in general the same
                    # between the source and destination sites but the page model needs
                    # to exist on both.
                    try:
                        model = apps.get_model(page_record['app_label'], page_record['model'])
                    except LookupError:
                        logging.error("Importing file failed because the model " + page_record[
                            'model'] + " does not exist on this environment.")
                        return (0, 1, "Importing file failed because the model " + page_record[
                            'model'] + " does not exist on this environment.")

                    specific_page = model.from_serializable_data(page_record['content'], check_fks=False,
                                                                 strict_fks=False)

                    base_page = pages_by_original_id[specific_page.id]
                    specific_page.page_ptr = base_page
                    specific_page.__dict__.update(base_page.__dict__)
                    specific_page.content_type = ContentType.objects.get_for_model(model)
                    update_page_references(specific_page, pages_by_original_id)
                    specific_page.save()

            return (len(contents) - len(existing_pages), len(existing_pages), error_msg)

        except LookupError as e:
            # If content.json does not exist, then return the error,
            # and terminate the import_page.
            logging.error("Importing file failed because file does not exist: " + str(e))
            traceback.print_exception(type(e), e, e.__traceback__)
            return (0, 1, "File does not exist: " + str(e))

    return (0, 1, "")


def list_existing_pages(pages):
    """
    Returns a list of pages that already exist in this
    environment by looking up by slug.

    Arguments:
    pages -- A list of pages in content.json

    Returns:
    existing_pages -- List of pages that correspond to indexes
    in 'pages'.
    """

    existing_pages = []

    for (i, page_record) in enumerate(pages):
        try:
            # Trying to get the page.
            localpage = Page.objects.get(slug=page_record['content']['slug'])

            if localpage:
                existing_pages.append(i)

        except Page.DoesNotExist:
            continue

    return existing_pages


def get_fileobject(title, objtype):
    """
    Returns the id of the object if it exists, otherwise returns
    False.

    Arguments:
    title -- The filename to be queried.
    objtype -- Image, Document from Wagtail.

    Returns:
    False if the object does not exist in this environment,
    object's integer ID if it does exist.
    """

    try:
        # Check whether the object already exists.
        localobj = objtype.objects.get(file=title)

        if localobj:
            return localobj.id

    except objtype.DoesNotExist:
        return False

    return False


def create_fileobject(title, uploaded_file, objtype):
    """
    Creates a new object given the information and returns
    the ID of the created object. Assumes the object with
    title does not exist.

    Arguments:
    title -- The filename of the object to be created.
    uploaded_file -- The file object to create.
    objtype -- Image, Document from Wagtail.

    Returns:
    Integer ID of the created object if the creation is successful;
    otherwise None.
    """

    try:
        with open(uploaded_file, 'rb') as mf:

            # Create the file object based on objtype.
            if objtype == File:
                filedata = File(mf, name=mf.name.split("/")[-1])
            elif objtype == Image:
                filedata = ImageFile(mf, name=mf.name.split("/")[-1])
            else:
                return None

            try:
                with transaction.atomic():
                    # Create the object and return the ID.
                    localobj = objtype.objects.create(file=filedata, title=title)
                    return localobj.id

            except IntegrityError:
                logging.error("Integrity error while uploading a file:", title)
                return None
    except FileNotFoundError:
        logging.error("File " + uploaded_file + " is not found on imported archive, skipping.")

    return None


def update_page_references(model, pages_by_original_id):
    """
    Updates the page references recursively.

    Arguments:
    model --
    pages_by_original_id --

    Returns:
    N/A. Overwrites model attributes.

    """

    for field in model._meta.get_fields():
        if isinstance(field, models.ForeignKey) and issubclass(field.related_model, Page):
            linked_page_id = getattr(model, field.attname)
            try:
                # see if the linked page is one of the ones we're importing
                linked_page = pages_by_original_id[linked_page_id]
            except KeyError:
                # any references to pages outside of the import should be left unchanged
                continue

            # update fk to the linked page's new ID
            setattr(model, field.attname, linked_page.id)

    # update references within inline child models, including the ParentalKey pointing back
    # to the page
    for rel in get_all_child_relations(model):
        for child in getattr(model, rel.get_accessor_name()).all():
            # reset the child model's PK so that it will be inserted as a new record
            # rather than updating an existing one
            child.pk = None
            # update page references on the child model, including the ParentalKey
            update_page_references(child, pages_by_original_id)
            