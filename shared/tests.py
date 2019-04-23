from wagtail.tests.utils import WagtailPageTests
from shared.test_utilities import assertPathDoesNotRedirectToTrailingSlash
from unittest.mock import MagicMock

class WagtailTests(WagtailPageTests):
    def setUp(self):
        pass

    def test_slashless_apis_are_good(self):
        # Doesn't pass if WAGTAIL_APPEND_SLASH = False is not set
        assertPathDoesNotRedirectToTrailingSlash(self, '/api/v2/pages/30')
