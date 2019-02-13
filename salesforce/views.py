from rest_framework import viewsets
from django.http import JsonResponse

from .models import School
from .serializers import SchoolSerializer

from salesforce.salesforce import Salesforce

class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer

def get_adoption_status(request):
    account = request.GET.get('id', False)
    print(account)
    if account:
        with Salesforce() as sf:
            q = sf.query("SELECT Adoption_Status__c FROM Contact WHERE Accounts_ID__c = '{}'".format(account))

            return JsonResponse(q)