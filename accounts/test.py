import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from django.conf import settings

USERNAME = 'openstax_cms_tester'
PASSWORD = 'openstax_cms_tester'

class Integration(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()
        

    @unittest.skip("web driver won't work on travis")
    def test_oauth_login(self):
        driver = self.driver
        driver.get("http://127.0.0.1:8000/accounts")
        if settings.APP_LOGIN_URL:
            self.assertEqual(driver.current_url,settings.APP_LOGIN_URL)
        else:
            self.assertEqual(driver.current_url,"http://127.0.0.1:8000/accounts/login/")
        connect_button=driver.find_element_by_name('connect')
        connect_button.click()
        self.assertIn("OpenStax Accounts", driver.title)
        username_field = driver.find_element_by_name("auth_key")
        username_field.send_keys(USERNAME)
        password_field = driver.find_element_by_name("password")
        password_field.send_keys(PASSWORD)
        driver.find_element_by_class_name("standard").click()
        self.assertIn(USERNAME,driver.page_source)
        logout_button = driver.find_element_by_id('openstax-logout')
        logout_button.click()
        if settings.APP_LOGOUT_URL:
            self.assertEqual(driver.current_url,settings.APP_LOGOUT_URL)
        else:
            self.assertEqual(driver.current_url,'http://127.0.0.1:8000/accounts/login/')
        driver.get("http://127.0.0.1:8000/accounts/profile")
        if settings.APP_LOGIN_URL:
            self.assertEqual(driver.current_url,settings.APP_LOGIN_URL)
        else:
            self.assertEqual(driver.current_url,'http://127.0.0.1:8000/accounts/login/?next=/accounts/profile/')
   
    def tearDown(self):
        self.driver.close()


