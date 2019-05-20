import os, logging
from django.core.management.base import BaseCommand
from wagtailimportexport.exporting import (
    export_pages,
    export_snippets,
    export_image_data,
    zip_content,
)
from wagtailimportexport.compat import Page

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Export Wagtail content (pages, snippets, images) to a file (default content.zip)'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--filename',
            default='content.zip',
            type=str,
            help='the filename for the exported content (default content.zip)',
        )
        parser.add_argument(
            '-a',
            '--all-pages',
            action="store_true",
            help='export all, including unpublished, pages',
        )
        parser.add_argument(
            '-n',
            '--null-users',
            action="store_true",
            help='null users in page and image data',
        )

    def handle(self, *args, **options):
        logger.debug(options)
        content_data = {
            'pages': export_pages(
                export_unpublished=options['all_pages'],
                null_users=options['null_users']),
            'snippets': export_snippets(),
            'images': export_image_data(null_users=options['null_users']),
        }
        fd = zip_content(content_data)
        with open(os.path.abspath(options['filename']), 'wb') as f:
            f.write(fd)
