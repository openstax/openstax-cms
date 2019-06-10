import json
import os
import tempfile
import zipfile
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User
from django.test import TestCase
from wagtailimportexport.compat import Page
from wagtailimportexport import views  # read this aloud

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
                            'haha': 'yup'
                        }
                    ]
                }
            }
        ]}

        views.null_pks(allpages)

        assert allpages['pages'][0]['content']['test'][0]['pk'] == None
        assert allpages['pages'][0]['content']['test'][0]['haha'] == 'yup'