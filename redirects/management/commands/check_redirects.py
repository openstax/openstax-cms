from django.core.management.base import BaseCommand
from wagtail.contrib.redirects.models import Redirect
import requests
import mail.functions as mail
import logging
import certifi


class Command(BaseCommand):
    help = "check all redirect URLs and email report of invalid URLs found"

    def handle(self, *args, **options):
        #supress urllib3 certificate error
        logging.getLogger("urllib3").setLevel(logging.CRITICAL)
        #get list of URLs
        redirects = Redirect.objects.all()
        bad_redirects = ''
        dev_email_info = ''
        USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'
        BAD_HTML_CODES = [404, 410, 500, 503]

        #Loop through and validate
        for re in redirects:
            try:
                response = requests.get(re.redirect_link, timeout=(10, 10), verify=certifi.where(), headers={ "user-agent": USER_AGENT})
                # if bad one is found, add short URL and redirect to list
                if response.status_code in BAD_HTML_CODES:
                    bad_redirects += re.old_path + ',' + re.redirect_link + '\n'
                    dev_email_info = self.add_to_dev_email(re, dev_email_info, response, exception=None)
            except Exception as e:
                bad_redirects += re.old_path + ',' + re.redirect_link + ' Exception: ' + str(e) + '\n'
                dev_email_info = self.add_to_dev_email(re, dev_email_info, response, exception=e)
                pass

        #email the list of bad URLs
        mail.send_redirect_report(bad_redirects)
        mail.send_dev_email('Redirect Report Additional Info', dev_email_info)

    def add_to_dev_email(self, redirect, dev_email_info, response, exception):
        dev_email_info += redirect.old_path + ',' + redirect.redirect_link + ', code: '
        if response is not None:
            dev_email_info += str(response.status_code)
        if exception is not None:
            dev_email_info += ', Exception: ' + str(exception)
        dev_email_info += '\n\n'
        return dev_email_info
