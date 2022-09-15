from .salesforce import Salesforce


def retrieve_salesforce_abbreviation(sf_book_name):
    if sf_book_name:
        with Salesforce() as sf:
            command = "Select Name from Book__c where Official_Name__c = '" + sf_book_name + "'"
            response = sf.query_all(command)
            book = response['records']
            sf_abbreviation = ''
            for record in book:
                sf_abbreviation = record['Name']
            return sf_abbreviation