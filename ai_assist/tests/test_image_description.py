from django.conf import settings
from django.test import TestCase


class ImageDescriptionConfigTests(TestCase):
    def test_image_description_uses_default_backend(self):
        # Alt text is high-volume, so it routes to the cheap "default" backend.
        self.assertEqual(
            settings.WAGTAIL_AI.get("IMAGE_DESCRIPTION_BACKEND"),
            "default",
        )


class ImageDescriptionRenditionTests(TestCase):
    def test_rendition_sent_to_the_llm_is_actually_jpeg(self):
        # wagtail-ai labels the upload "image/jpeg" no matter what it sends, and
        # Anthropic 400s when the bytes disagree.
        import io

        from django.core.files.images import ImageFile
        from PIL import Image as PILImage
        from wagtail.images import get_image_model
        from wagtail_ai.context import image_validator

        buf = io.BytesIO()
        PILImage.new("RGBA", (64, 64)).save(buf, "PNG")
        image = get_image_model().objects.create(
            title="test", file=ImageFile(buf, name="test.png")
        )

        with image_validator({"image": str(image.pk)}).open() as f:
            self.assertEqual(f.read(2), b"\xff\xd8")
