import json
import os
import tempfile
import zipfile
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User
from django.test import TestCase, Client 
from wagtail.tests.utils import WagtailTestUtils
from wagtailimportexport.compat import Page
from django.urls import reverse
from wagtailimportexport import views  # read this aloud

class TestClass(object):
    pass

class TestViews(TestCase):
    def test_null_pks(self):
        """
        Testing null_pk method.
        """

        allpages = {'pages': [
            {
                'content': {
                    'test': [
                        {
                            'pk': 12,
                            'haha': 'yup',
                            'link_document': 'omg'
                        }
                    ]
                }
            }
        ]}

        views.null_pks(allpages)

        assert allpages['pages'][0]['content']['test'][0]['pk'] == None
        assert allpages['pages'][0]['content']['test'][0]['haha'] == 'yup'
        assert allpages['pages'][0]['content']['test'][0]['link_document'] == None

    def test_null_pks_form(self):
        """
        Testing null_pk method.
        """

        form = TestClass()
        setattr(form, 'cleaned_data', {
            'new_title': 'test2',
            'new_slug': 'test2'
        })

        allpages = {'pages': [
            {
                'content': {
                    'test': [
                        {
                            'pk': 12,
                            'haha': 'yup'
                        }
                    ],
                    'title': 'test',
                    'slug': 'test',
                    'draft_title': 'test'
                }
            }
        ]}

        views.null_pks(allpages, form)

        assert allpages['pages'][0]['content']['test'][0]['pk'] == None
        assert allpages['pages'][0]['content']['test'][0]['haha'] == 'yup'
        assert allpages['pages'][0]['content']['title'] == 'test2'
        assert allpages['pages'][0]['content']['draft_title'] == 'test2'
        assert allpages['pages'][0]['content']['slug'] == 'test2'

class TestForms(TestCase, WagtailTestUtils):
    def setUp(self):
        self.user = self.login()
 
    def test_importfile(self):
        response = self.client.get(reverse('wagtailimportexport_admin:import_from_file'))
        self.assertNotEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'wagtailimportexport/import_from_file.html')
    
    def test_exportfile(self):
        response = self.client.get(reverse('wagtailimportexport_admin:export_to_file'))
        self.assertNotEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'wagtailimportexport/export_to_file.html')

    def test_duplicate(self):
        response = self.client.get(reverse('wagtailimportexport_admin:duplicate', args=[1]))
        self.assertNotEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'wagtailimportexport/duplicate.html')

    def test_index(self):
        response = self.client.get(reverse('wagtailimportexport_admin:index'))
        self.assertNotEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'wagtailimportexport/index.html')