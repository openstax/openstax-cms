import re
import unittest
from django.test import TestCase
from django.test import override_settings
from django.conf import settings
from selenium import webdriver
import shutil
import os
from django.test import LiveServerTestCase
from wagtail.tests.utils import WagtailPageTests


exempt_urls = ['http://localhost:8001/admin/',
               'http://localhost:8001/',
               'http://localhost:8001/django-admin/',
               ]
not_exempt_urls = ['http://localhost:8001/api',
                   'http://localhost:8001/api/',
                   'http://localhost:8001/api/user',
                   ]
HTTP_TEST_HOST = 'localhost:8001'


class sslConnections(LiveServerTestCase, WagtailPageTests):
    GUI = False

    def test_exempt_patterns(self):
        exempt_patterns = settings.SECURE_REDIRECT_EXEMPT
        for url in exempt_urls:
            MATCH_FOUND = False
            for pattern in exempt_patterns:
                prog = re.compile(pattern)

                if prog.match(url):
                    MATCH_FOUND = True
                    break
            self.assertTrue(MATCH_FOUND)

    def test_non_exempt_patterns(self):
        exempt_patterns = settings.SECURE_REDIRECT_EXEMPT
        for url in not_exempt_urls:
            MATCH_FOUND = False
            for pattern in exempt_patterns:
                prog = re.compile(pattern)
                if prog.fullmatch(url):
                    fail_message = "\n url '{0}' match pattern '{1}':"\
                                   "\n{2}".format(
                                       url, pattern, str(prog.match(url)))
                    self.fail(fail_message)

    def setUp(self):
        super(WagtailPageTests, self).setUp()
        super(LiveServerTestCase, self).setUp()
        if self.GUI:
            self.driver = webdriver.Firefox()
        else:
            try:
                phantomjs_path = os.environ['phantomjs']
            except KeyError:
                phantomjs_path = shutil.which("phantomjs")
            self.driver = webdriver.PhantomJS(executable_path=phantomjs_path)

    def tearDown(self):
        self.driver.close()
        super(WagtailPageTests, self).tearDown()
        super(LiveServerTestCase, self).tearDown()

    def test_unprotected_urls(self):
        for url in exempt_urls:
            response = self.client.get(url,
                                       follow=False,
                                       HTTP_HOST=HTTP_TEST_HOST)
            self.assertEqual(response.status_code, 200)

    def test_protected_urls(self):

        for url in not_exempt_urls:
            response = self.client.get(url,
                                       follow=False,
                                       HTTP_HOST=HTTP_TEST_HOST)
            self.assertEqual(response.status_code, 301)
            self.assertIn('https', response.url)


