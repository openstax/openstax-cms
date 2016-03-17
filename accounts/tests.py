from django.test import TestCase
from django.test import LiveServerTestCase
from wagtail.tests.utils import WagtailPageTests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import models
from django.core.exceptions import ObjectDoesNotExist
import unittest
import shutil
import os
from django.test import TestCase, override_settings
from django.contrib.auth.models import Group
import logging


# class Integration(LiveServerTestCase, WagtailPageTests):
#     serialized_rollback = True
#
#     def setUp(self):
#         super(WagtailPageTests, self).setUp()
#         super(LiveServerTestCase, self).setUp()
#         try:
#             phantomjs_path = os.environ['phantomjs']
#         except KeyError:
#             phantomjs_path = shutil.which("phantomjs")
#         self.driver = webdriver.PhantomJS(executable_path=phantomjs_path)
#
#     def target(self, username, password):
#         if User.objects.filter(username=username).exists():
#             User.objects.get(username=username).delete()
#         self.assertFalse(User.objects.filter(username=username).exists())
#         driver = self.driver
#         driver.get("http://localhost:8001/admin")
#         self.assertEqual(
#            driver.current_url, 'http://localhost:8001/admin/login/?next=/admin/')
#         connect_button = driver.find_element_by_xpath('/html/body/div[1]/a')
#         connect_button.click()
#         username_field = driver.find_element_by_name("auth_key")
#         username_field.send_keys(username)
#         password_field = driver.find_element_by_name("password")
#         password_field.send_keys(password)
#         sign_in_button = driver.find_element_by_class_name("standard")
#         sign_in_button.click()
#         self.assertEqual(
#            driver.current_url, 'http://localhost:8001/admin/login/?next=/admin/')
#         self.assertTrue(User.objects.filter(username=username).exists())
#         return User.objects.get(username=username)
#
#     def test_oauth_login_create_user(self):
#         USERNAME = 'openstax_cms_tester'
#         PASSWORD = 'openstax_cms_tester'
#         user = self.target(USERNAME, PASSWORD)
#         self.assertEqual(user.username, USERNAME)
#         self.assertFalse(user.is_superuser)
#         self.assertFalse(user.is_staff)
#         self.assertTrue(user.is_active)
#         self.driver.get('http://localhost:8001/api/user/?format=json')
#         self.assertNotIn("Faculty", self.driver.page_source)
#
#     def test_faculty_verification(self):
#         USERNAME = 'openstax_cms_faculty_tester'
#         PASSWORD = 'openstax_cms_faculty_tester'
#         user = self.target(USERNAME, PASSWORD)
#         self.driver.get('http://localhost:8001/api/user/?format=json')
#         self.assertTrue(user.groups.filter(name="Faculty").exists())
#
#     def tearDown(self):
#         self.driver.close()
#         super(WagtailPageTests, self).tearDown()
#         super(LiveServerTestCase, self).tearDown()



