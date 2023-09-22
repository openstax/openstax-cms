from unittest import mock

from django.forms import FileField, ModelChoiceField
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File

from pages.models import HomePage
from wagtailimportexport.forms import ImportPage, ExportPage


class TemplateTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_import_template(self):
        response = self.client.get('/admin/import-export/import-page/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_export_template(self):
        response = self.client.get('/admin/import-export/export-page/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_import_form(self):
        zip = SimpleUploadedFile("test.zip", b"file content", content_type="application/zip")
        form_data = {"parent_page": 1}
        form = ImportPage(form_data, files={'file': zip})
        self.assertTrue(form.is_valid(), form.errors)

    def test_export_form(self):
        form_data = {"root_page": 1}
        form = ExportPage(form_data)
        self.assertTrue(form.is_valid(), form.errors)



