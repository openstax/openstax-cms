import os

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from wagtail.images import get_image_model
from willow.image import Image as WillowImage

from books.models import Book

Image = get_image_model()


def _image_from_document(document, default_title):
    """Create a Wagtail Image from a Document's file, computing dimensions
    (Willow handles raster + SVG). Returns the saved Image."""
    document.file.open('rb')
    try:
        content = document.file.read()
    finally:
        document.file.close()

    width, height = WillowImage.open(ContentFile(content)).get_size()

    image = Image(title=(document.title or default_title)[:255])
    image.file.save(os.path.basename(document.file.name), ContentFile(content), save=False)
    # Set dimensions AFTER file.save: Wagtail's image field runs
    # update_dimension_fields during save and would otherwise null them out
    # (it reads the already-consumed ContentFile). int() because Willow returns
    # floats for SVG dimensions, while Image.width/height are integer fields.
    image.width = int(width)
    image.height = int(height)
    image.save()
    return image


class Command(BaseCommand):
    help = "Convert legacy Book cover/title_image Documents into Wagtail Images (idempotent)."

    def handle(self, *args, **options):
        converted_cover = converted_banner = skipped = errored = 0
        # select_related avoids a query per Document lookup (cover/title_image);
        # iterator() keeps memory bounded on the full books table.
        books = Book.objects.select_related('cover', 'title_image').order_by('id').iterator()
        for book in books:
            updates = {}
            try:
                if book.cover_id and not book.cover_image_id:
                    updates['cover_image'] = _image_from_document(book.cover, f'{book.title} cover')
                if book.title_image_id and not book.banner_image_id:
                    updates['banner_image'] = _image_from_document(book.title_image, f'{book.title} title image')
            except Exception as e:
                # One bad legacy file (missing blob, corrupt image/SVG, etc.)
                # shouldn't block conversion for every other book.
                self.stderr.write(self.style.WARNING(
                    f"Skipping book {book.pk} ({book.title!r}): {e}"))
                errored += 1
                continue
            if updates:
                converted_cover += 'cover_image' in updates
                converted_banner += 'banner_image' in updates
                # Direct column update: avoids Book.save() side effects
                # (Salesforce sync, field broadcasts) — we only set the FKs.
                Book.objects.filter(pk=book.pk).update(**updates)
            else:
                skipped += 1
        self.stdout.write(self.style.SUCCESS(
            f"Converted {converted_cover} covers, {converted_banner} banners; "
            f"{skipped} books unchanged; {errored} books errored."))
