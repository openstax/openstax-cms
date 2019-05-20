from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from modelcluster.models import get_all_child_relations

from wagtailimportexport.compat import Page


@transaction.atomic()
def import_pages(import_data, parent_page):
    """
    Take a JSON export of part of a source site's page tree
    and create those pages under the parent page
    """
    pages_by_original_path = {}
    pages_by_original_id = {}

    # First create the base Page records; these contain no foreign keys, so this allows us to
    # build a complete mapping from old IDs to new IDs before we go on to importing the
    # specific page models, which may require us to rewrite page IDs within foreign keys / rich
    # text / streamfields.
    page_content_type = ContentType.objects.get_for_model(Page)
    for (i, page_record) in enumerate(import_data['pages']):
        # build a base Page instance from the exported content (so that we pick up its title and other
        # core attributes)
        page = Page.from_serializable_data(page_record['content'])
        original_path = page.path
        original_id = page.id

        # clear id and treebeard-related fields so that they get reassigned when we save via add_child
        page.id = None
        page.path = None
        page.depth = None
        page.numchild = 0
        page.url_path = None
        page.content_type = page_content_type
        if i == 0:
            parent_page.add_child(instance=page)
        else:
            # Child pages are created in the same sibling path order as the
            # source tree because the export is ordered by path
            parent_path = original_path[:-(Page.steplen)]
            pages_by_original_path[parent_path].add_child(instance=page)

        pages_by_original_path[original_path] = page
        pages_by_original_id[original_id] = page

    for (i, page_record) in enumerate(import_data['pages']):
        # Get the page model of the source page by app_label and model name
        # The content type ID of the source page is not in general the same
        # between the source and destination sites but the page model needs
        # to exist on both.
        # Raises LookupError exception if there is no matching model
        model = apps.get_model(page_record['app_label'], page_record['model'])

        specific_page = model.from_serializable_data(page_record['content'], check_fks=False, strict_fks=False)
        base_page = pages_by_original_id[specific_page.id]
        specific_page.page_ptr = base_page
        specific_page.__dict__.update(base_page.__dict__)
        specific_page.content_type = ContentType.objects.get_for_model(model)
        update_page_references(specific_page, pages_by_original_id)
        specific_page.save()

    return len(import_data['pages'])


def update_page_references(model, pages_by_original_id):
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
