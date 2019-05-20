import json
import os
import tempfile
import zipfile
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User
from django.test import TestCase
from wagtail_factories import ImageFactory
from wagtailimportexport.compat import Page
from wagtailimportexport import exporting  # read this aloud
from testapp.models import TestSnippet


class TestExportingPages(TestCase):
    def test_export_pages(self):
        """exporting pages with no options returns in a list of all published pages."""
        root_page = Page.objects.first()
        new_page = Page(title="This is the New Page", slug="new-page")
        root_page.add_child(instance=new_page)
        page_data = exporting.export_pages()
        page_json = json.dumps(page_data, cls=DjangoJSONEncoder, indent=2)
        assert new_page.title in page_json

    def test_export_unpublished(self):
        """exporting with export_unpublished=True exports unpublished pages."""
        root_page = Page.objects.first()
        new_page = Page(title="This is the New Page", slug="new-page")
        root_page.add_child(instance=new_page)
        new_page.unpublish()

        page_data = exporting.export_pages(
        )  # default export_unpublished=False
        page_json = json.dumps(page_data, cls=DjangoJSONEncoder)
        assert new_page.title not in page_json

        page_data = exporting.export_pages(export_unpublished=True)
        page_json = json.dumps(page_data, cls=DjangoJSONEncoder)
        assert new_page.title in page_json

    def test_export_null_users(self):
        """exporting with null_users=True nulls the user ids in the data."""
        user = User.objects.create(username='TEST USER')
        root_page = Page.objects.first()
        new_page = Page(
            title="This is the New Page", slug="new-page", owner=user)
        root_page.add_child(instance=new_page)

        page_data = exporting.export_pages()  # default null_users=False
        page_json = json.dumps(page_data, cls=DjangoJSONEncoder)
        assert '"owner": %d' % user.pk in page_json

        page_data = exporting.export_pages(null_users=True)
        page_json = json.dumps(page_data, cls=DjangoJSONEncoder)
        assert '"owner": %d' % user.pk not in page_json


class TestExportingSnippets(TestCase):
    def test_export_snippets(self):
        """exporting snippets returns a list of all snippets in the database"""
        snippet = TestSnippet.objects.create(text="Hi, folks, Snippy here.")
        snippet_data = exporting.export_snippets()
        snippet_json = json.dumps(snippet_data, cls=DjangoJSONEncoder)
        assert '"text": "%s"' % snippet.text in snippet_json


class TestExportingImages(TestCase):
    def test_export_images(self):
        """exporting image data returns a list of images in the database"""
        image = ImageFactory(title="Very blue.")
        image_data = exporting.export_image_data()
        image_json = json.dumps(image_data, cls=DjangoJSONEncoder)
        assert '"title": "%s"' % image.title in image_json

    def test_export_images_null_user(self):
        """exporting images with null_users=True nulls the uploaded_by_user_id field"""
        user = User.objects.create(username='TEST USER')
        image = ImageFactory(title="Very blue.", uploaded_by_user=user)

        image_data = exporting.export_image_data()  # default null_users=False
        image_json = json.dumps(image_data, cls=DjangoJSONEncoder)
        assert '"title": "%s"' % image.title in image_json
        assert '"uploaded_by_user_id": %d' % user.pk in image_json

        image_data = exporting.export_image_data(null_users=True)
        image_json = json.dumps(image_data, cls=DjangoJSONEncoder)
        assert len(image_data) == 1
        assert '"title": "%s"' % image.title in image_json
        assert '"uploaded_by_user_id": %d' % user.pk not in image_json
        assert '"uploaded_by_user_id": null' in image_json


class TestExportingZipContent(TestCase):
    def test_export_zip(self):
        """exporting content zip should result in a zip file containing content.json and images"""
        root_page = Page.objects.first()
        new_page = Page(
            title="This is the New Page", slug="new-page")
        root_page.add_child(instance=new_page)
        image = ImageFactory(title="Very blue.")
        snippet = TestSnippet.objects.create(text="Hi, folks, Snippy here.")
        content_data = {
            'pages': exporting.export_pages(),
            'snippets': exporting.export_snippets(),
            'images': exporting.export_image_data(),
        }
        zip_data = exporting.zip_content(content_data)
        with tempfile.TemporaryDirectory() as tempdir:
            zipfilename = os.path.join(tempdir, 'content.zip')
            with open(zipfilename, 'wb') as f:
                f.write(zip_data)
            with zipfile.ZipFile(zipfilename, 'r') as zf:
                assert 'content.json' in zf.namelist()
                content_json = zf.read('content.json').decode('utf-8')

        assert '"pages":' in content_json
        assert '"images":' in content_json
        assert '"snippets"' in content_json
        content_data = json.loads(content_json)
        assert len(content_data['pages']) > 1
        assert len(content_data['images']) == 1
        assert len(content_data['snippets']) == 1
