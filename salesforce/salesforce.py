from simple_salesforce import Salesforce as SimpleSalesforce
from django.conf import settings
from contextlib import ContextDecorator
import logging
import sys
logger = logging.getLogger('accounts.salesforce')


class Salesforce(SimpleSalesforce, ContextDecorator):

    def __init__(self):
        try:
            super(Salesforce, self).__init__(**settings.SALESFORCE)
        except:
            self.__exit__(*sys.exc_info())

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        if not exc == (None, None, None):
            (exc_type, exc, exc_tb) = exc
            error_type = exc_type.__name__
            error_message = str(exc)
            logger.error("{0}('{1}')".format(error_type, error_message))
        return False

    def faculty_status(self, accounts_id):
        command = "SELECT Faculty_Verified__c FROM Contact WHERE Accounts_ID__c = '{0}'".format(
            accounts_id)

        contact_info = self.query(command)
        # each accounts key should be unique
        if contact_info['totalSize'] == 1:
            status = contact_info['records'][0]['Faculty_Verified__c']
            return status

