from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse, Http404
from django.utils import timezone

from .models import School, AdoptionOpportunityRecord, Partner, SalesforceForms
from .serializers import SchoolSerializer, AdoptionOpportunityRecordSerializer, PartnerSerializer, SalesforceFormsSerializer

from salesforce.salesforce import Salesforce

class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer


class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.filter(visible_on_website=True)
    serializer_class = PartnerSerializer


class SalesforceFormsViewSet(viewsets.ModelViewSet):
    queryset = SalesforceForms.objects.all()
    serializer_class = SalesforceFormsSerializer


class AdoptionOpportunityRecordViewSet(viewsets.ModelViewSet):
    serializer_class = AdoptionOpportunityRecordSerializer

    def get_queryset(self):
        queryset = AdoptionOpportunityRecord.objects.filter(updated=False)
        account_id = self.request.query_params.get('account_id', None)
        if account_id is not None:
            queryset = queryset.filter(account_id=account_id)
        else:
            queryset = None # if no account id, return nothing
        return queryset


class AdoptionUpdated(APIView):
    def post(self, request, account_id):
        # if no model exists by this PK, raise a 404 error
        records = AdoptionOpportunityRecord.objects.filter(account_id=account_id)
        if not records:
            return JsonResponse({'error': 'No records associated with that ID.'})

        for record in records:
            # this is the only field we want to update
            data = {"updated": True}
            serializer = AdoptionOpportunityRecordSerializer(record, data=data, partial=True)

            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse(data)


def get_adoption_status(request):
    account = request.GET.get('id', False)

    if account:
        with Salesforce() as sf:
            q = sf.query("SELECT Adoption_Status__c FROM Contact WHERE Accounts_ID__c = '{}'".format(account))

            return JsonResponse(q)
    else:
        raise Http404('Must supply account id for adoption.')
