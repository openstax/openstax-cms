from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse

from .models import School, AdoptionOpportunityRecord
from .serializers import SchoolSerializer, AdoptionOpportunityRecordSerializer

from salesforce.salesforce import Salesforce

class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer


class AdoptionOpportunityRecordViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = AdoptionOpportunityRecordSerializer

    def get_queryset(self):
        queryset = AdoptionOpportunityRecord.objects.all()
        account_id = self.request.query_params.get('account_id', None)
        if account_id is not None:
            queryset = queryset.filter(account_id=account_id)
        else:
            queryset = None # if no account id, return nothing
        return queryset


def get_adoption_status(request):
    account = request.GET.get('id', False)

    if account:
        with Salesforce() as sf:
            q = sf.query("SELECT Adoption_Status__c FROM Contact WHERE Accounts_ID__c = '{}'".format(account))

            return JsonResponse(q)
