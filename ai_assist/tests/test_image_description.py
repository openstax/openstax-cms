from django.conf import settings
from django.test import TestCase


class ImageDescriptionConfigTests(TestCase):
    def test_image_description_uses_default_backend(self):
        # Alt text is high-volume, so it routes to the cheap "default" backend.
        self.assertEqual(
            settings.WAGTAIL_AI.get("IMAGE_DESCRIPTION_BACKEND"),
            "default",
        )
