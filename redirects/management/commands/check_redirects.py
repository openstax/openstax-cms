from django.core.management.base import BaseCommand
from wagtail.contrib.redirects.models import Redirect
import requests
import mail.functions as mail
import logging


class Command(BaseCommand):
    help = "check all redirect URLs and email report of invalid URLs found"

    def handle(self, *args, **options):
        #supress urllib3 certificate error
        logging.getLogger("urllib3").setLevel(logging.CRITICAL)
        #get list of URLs
        redirects = Redirect.objects.all()
        bad_redirects = ''

        #Loop through and validate
        for re in redirects:
            try:
                response = requests.get(re.redirect_link, timeout=10)
                # if bad one is found, add short URL and redirect to list
                if response.status_code != 200:
                    bad_redirects += re.old_path + ',' + re.redirect_link + '\n'
            except:
                bad_redirects += re.old_path + ',' + re.redirect_link + '\n'
                pass

        #email the list of bad URLs
        mail.send_redirect_report(bad_redirects)