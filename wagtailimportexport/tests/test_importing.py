import json
import os
import tempfile
import zipfile
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User
from django.test import TestCase
from wagtailimportexport.compat import Page
from wagtailimportexport import importing  # read this aloud

class TestImportingPages(TestCase):
    def test_importing(self):
        parent_page = Page.objects.first()
        allpages = {
            "pages": [
                {
                "app_label": "pages",
                "model": "contactus",
                "documents": {},
                "images": {
                    "promote_image": None
                },
                "content": {
                    "expire_at": None,
                    "locked": False,
                    "first_published_at": "2016-06-23T15:25:21.881Z",
                    "owner": None,
                    "tagline": "If you have any questions or feedback, drop us a line!",
                    "numchild": 0,
                    "pk": 89,
                    "mailing_header": "Mailing Address",
                    "depth": 3,
                    "seo_title": "",
                    "content_type": 32,
                    "expired": False,
                    "live": True,
                    "promote_image": None,
                    "show_in_menus": False,
                    "go_live_at": None,
                    "mailing_address": "<h3>OpenStax</h3><p>Rice University<br/>6100 Main Street MS-375<br/>Houston, TX 77005</p>",
                    "title": "Contact Us",
                    "live_revision": 5575,
                    "path": "000100010004",
                    "slug": "contact",
                    "customer_service": "<p><b>Need help?</b><br/>Visit our <a href=\"https://openstax.org/support\">Support Center</a>.<br/></p>",
                    "url_path": "/openstax-homepage/contact/",
                    "draft_title": "Contact Us",
                    "has_unpublished_changes": False,
                    "last_published_at": "2018-10-23T02:12:47.898Z",
                    "search_description": "",
                    "latest_revision_created_at": "2018-10-23T02:12:47.861Z"
                }
                }
            ]
        }

        importing.import_pages(allpages, parent_page, None)

        page = Page.objects.filter(slug="contact").first()

        assert(page.slug == "contact")