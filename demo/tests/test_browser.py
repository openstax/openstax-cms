from unittest import SkipTest
from django.test import LiveServerTestCase
from django.contrib.auth.models import User

from selenium import webdriver
from selenium.common.exceptions import WebDriverException


class AdminTestCase(LiveServerTestCase):

    def setUp(self):
        User.objects.create_superuser(
            username='admin',
            password='admin',
            email='admin@example.com'
        )

        try:
            self.selenium = webdriver.Firefox()
        except(WebDriverException):
            raise SkipTest("webdriver failed. "
                           "Check if selenium is installed in FireFox")

        self.selenium.maximize_window()
        super(AdminTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(AdminTestCase, self).tearDown()

    def test_admin_user(self):
        """
        Django admin create user test
        This test will create a user in django admin and assert that
        page is redirected to the new user change form.
        """

        self.selenium.get(self.live_server_url + "/admin/")

        username = self.selenium.find_element_by_id("id_username")
        username.send_keys("admin")
        password = self.selenium.find_element_by_id("id_password")
        password.send_keys("admin")
        sign_in = self.selenium.find_element_by_xpath(
            '//input[@value="Sign in"]')
        sign_in.click()

        self.selenium.get(self.live_server_url + "/admin/users/")

        users_table = self.selenium.find_elements_by_xpath(
            '//*[@id="user-results"]/table/tbody/tr/td')

        returned_dict = [{'name': users_table[i].text,
                          'username': users_table[i + 1].text,
                          'level': users_table[i + 2].text,
                          'status': users_table[i + 3].text}
                         for i in range(0, len(users_table), 4)]

        expected_dict = {
            'username': u'admin',
            'status': u'Active',
            'name': u'admin',
            'level': u'Admin'}

        self.assertIn(expected_dict, returned_dict)

        self.selenium.get(self.live_server_url + "/admin/logout/")


