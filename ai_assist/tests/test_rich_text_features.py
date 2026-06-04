from django.conf import settings
from django.test import TestCase


class RichTextAIFeatureTests(TestCase):
    """Guard the root cause of the missing AI magic-wand control.

    wagtail-ai appends its "ai" Draftail control to `default_features`, but this
    project pins an EXPLICIT features list in WAGTAILADMIN_RICH_TEXT_EDITORS,
    which overrides default_features. If "ai" is dropped from that list, the
    wand silently disappears from every rich-text editor.
    """

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
