from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse, Http404
from django.utils import timezone

from .models import School, AdoptionOpportunityRecord, Partner, SalesforceForms, ResourceDownload
from .serializers import SchoolSerializer, AdoptionOpportunityRecordSerializer, PartnerSerializer, SalesforceFormsSerializer, ResourceDownloadSerializer

from salesforce.salesforce import Salesforce
from books.models import Book

class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer


class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.filter(visible_on_website=True)
    serializer_class = PartnerSerializer


class SalesforceFormsViewSet(viewsets.ModelViewSet):
    queryset = SalesforceForms.objects.all()
    serializer_class = SalesforceFormsSerializer

class ResourceDownloadViewSet(viewsets.ModelViewSet):
    queryset = ResourceDownload.objects.all()
    serializer_class = ResourceDownloadSerializer


class AdoptionOpportunityRecordViewSet(viewsets.ViewSet):
    def list(self, request, account_id):
        queryset = AdoptionOpportunityRecord.objects.filter(account_id=account_id)
        serializer = AdoptionOpportunityRecordSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, account_id, format=None):
        records = AdoptionOpportunityRecord.objects.filter(account_id=account_id)
        if not records:
            return JsonResponse({'error': 'No records associated with that ID.'})

        for record in records:
            verified = self.request.data.get('verified', None)
            confirmed_yearly_students = self.request.data.get('confirmed_yearly_students', 0)
            data = {"verified": verified, "confirmed_yearly_students": confirmed_yearly_students}
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
