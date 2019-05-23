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
    pass