from django.conf import settings
from django.test import TestCase


class RichTextAIFeatureTests(TestCase):
    # The explicit features list overrides wagtail-ai's default; 'ai' must stay in it.
    def test_default_editor_features_include_ai(self):
        features = settings.WAGTAILADMIN_RICH_TEXT_EDITORS["default"]["OPTIONS"][
            "features"
        ]
        self.assertIn(
            "ai",
            features,
            msg="'ai' must be in the default rich-text features or the wagtail-ai "
            "magic-wand control will not appear in the editor toolbar.",
        )
