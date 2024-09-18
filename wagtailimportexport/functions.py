import tempfile
import zipfile
import os
import io
import json
import logging

from django.core.files.storage import storages as get_storage_class
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.reverse_related import ManyToOneRel
from django.contrib.contenttypes.models import ContentType

from wagtail.fields import StreamField
from wagtail.documents.models import Document


def null_pks(page, data):
    """
    Nullifies primary keys within all supplied fields.

    Arguments:
    page -- Page object.
    data -- Page object in dictionary format.

    Returns:
    N/A. Overwrites the argument.
    """

    # Nullify the main ID
    data['id'] = None
    data['pk'] = None

    # Loop through all fields.
    for field_name, field_val in data.items():
        if type(field_val) != list:
            continue

        for i, sub_item in enumerate(field_val):
            if 'pk' in sub_item:
                data[field_name][i]['pk'] = None


def find_null_child_blocks(subfield, location, data):
    """
    Recursive function to find all children blocks
    within streamfield and nullify fks.

    Arguments:
    subfield -- A field.
    location -- (Ordered) list of field keys that act
                as a tree.
    data -- Data object to overwrite the changes to.

    Returns:
    N/A. Overwrites data.
    """

    # Some fields do not have child_blocks, and we should not
    # investigate further if that's the case.
    if "child_blocks" in subfield.__dict__.keys():

        # Go through all fields.
        for field_key, field_val in subfield.child_blocks.items():

            # We want to catch the ForeignKey
            if isinstance(field_val, ForeignKey):
                # TODO: Implement overwriting.
                pass

            # Recursive Calls
            find_null_child_blocks(field_val, location + [field_key], data)


def find_null_child_relations(subfield, location, data):
    """
    Recursive function to find all children relations
    within manyotoone relationships and nullify fks.

    Arguments:
    subfield -- A field.
    location -- (Ordered) list of field keys that act
                as a tree.
    data -- Data object to overwrite the changes to.

    Returns:
    N/A. Overwrites data.
    """

    # Some fields do not have related_model, and we should not
    # investigate further if that's the case.
    if "related_model" in subfield.__dict__.keys():

        # Go through all fields.
        for field in subfield.related_model._meta.fields:

            # We want to catch the ForeignKey
            if isinstance(field, ForeignKey):
                if not location[0] in data:
                    continue

                for i, value in enumerate(data[location[0]]):
                    if not field.name in data[location[0]][i]:
                        continue

                    data[location[0]][i][field.name] = None


def null_fks(page, data):
    """
    Nullifies foreign keys within all supplied fields.

    Arguments:
    page -- Page object.
    data -- Page object in dictionary format.

    Returns:
    N/A. Overwrites the argument.
    """

    # Loop through all fields.
    for field in page._meta.get_fields():

        # Check whether the field is a ForeignKey.
        # By nature, owner, content_type, live_revision
        # are foreign keys defined by wagtail core pages.
        if (isinstance(field, ForeignKey)):
            data[field.name] = None

        # StreamFields often have foreign keys associated with them.
        # if(isinstance(field, StreamField)):
        #     find_null_child_blocks(field.stream_block, [field.name], data)
        #
        # # Many to One relations often have foreign keys associated with them.
        # if(isinstance(field, ManyToOneRel)):
        #     find_null_child_relations(field, [field.name], data)


def zip_contents(page_contents):
    """
    Creates and returns a zip archive of all supplied items.

    Arguments:
    page_contents -- A list of page dictionaries.

    Returns:
    Zip file to be downloaded by the client.
    """

    file_storage = get_storage_class()()

    # Create a temporary directory.
    with tempfile.TemporaryDirectory() as tempdir:

        # Create a temporary zip.
        zfname = os.path.join(tempdir, 'content.zip')

        # Open the zip archive with write mode.
        with zipfile.ZipFile(zfname, 'w') as zf:

            # Write the main content.json file to store all data.
            zf.writestr(
                'content.json',
                json.dumps(page_contents, indent=2, cls=DjangoJSONEncoder)
            )

            # Loop through pages to explore all used images and documents.
            for page in page_contents:

                # Export all the images.
                for image_def in page['images'].values():
                    if not image_def:
                        continue

                    filename = image_def['file']['name']

                    try:
                        with file_storage.open(filename, 'rb') as f:
                            zf.writestr(filename, f.read())
                    except FileNotFoundError:
                        logging.error("File " + str(filename) + " is not found on local file storage and was not exported.")

                # Export all the documents.
                for doc_def in page['documents'].values():
                    if not doc_def:
                        continue

                    filename = doc_def['file']['name']

                    try:
                        with file_storage.open(filename, 'rb') as f:
                            zf.writestr(filename, f.read())
                    except FileNotFoundError:
                        logging.error("File " + str(filename) + " is not found on local file storage and was not exported.")

        with open(zfname, 'rb') as zf:
            fd = zf.read()

    return io.BytesIO(fd)


def unzip_contents(zip_contents):
    """
    Extracts all items in the zip archive and returns a mapping
    of the contents, as well as their location in tempdir.

    Arguments:
    zip_contents -- Zip file that is in memory.

    Returns:
    Map of the extracted files.
    """

    # Create a temporary directory.
    tempdir = tempfile.mkdtemp()

    # Extract all contents.
    zip_contents.extractall(tempdir)

    # Return the mapping of all extracted members.
    return {member: tempdir + '/' + member for member in zip_contents.namelist()}


def document_title(doc_pk):
    doc = Document.objects.all().filter(pk=doc_pk)
    if not doc:
        return None
    else:
        return str(doc[0])


def document_id(doc_title):
    doc = Document.objects.all().filter(title=doc_title)
    if not doc:
        return None
    else:
        return doc[0].pk


def content_type_by_model(model):
    content_type = ContentType.objects.all().filter(model=model)
    if not content_type:
        return None
    else:
        return str(content_type[0].pk)

