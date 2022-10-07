from .salesforce import Salesforce


def retrieve_salesforce_names(sf_book_id):
    if sf_book_id:
        with Salesforce() as sf:
            command = "Select Name, Official_Name__c from Book__c where Id = '" + sf_book_id + "'"
            response = sf.query_all(command)
            book = response['records']
            sf_names = {}
            for record in book:
                sf_names['Name'] = record['Name']
                sf_names['Official_Name'] = record['Official_Name__c']
            return sf_names