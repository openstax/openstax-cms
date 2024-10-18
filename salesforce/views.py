from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.core.exceptions import MultipleObjectsReturned

from .models import School, AdoptionOpportunityRecord, Partner, SalesforceForms, ResourceDownload, SavingsNumber
from .serializers import SchoolSerializer, PartnerSerializer, SalesforceFormsSerializer, ResourceDownloadSerializer, SavingsNumberSerializer

from salesforce.salesforce import Salesforce


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name',]


class PartnerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Partner.objects.filter(visible_on_website=True)
    serializer_class = PartnerSerializer


class SalesforceFormsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SalesforceForms.objects.all()
    serializer_class = SalesforceFormsSerializer


class ResourceDownloadViewSet(viewsets.ModelViewSet):
    queryset = ResourceDownload.objects.all()
    serializer_class = ResourceDownloadSerializer

    def perform_create(self, serializer):
        serializer.save(last_access=timezone.now())


class SavingsNumberViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This endpoint will only ever return one item, the latest updated savings.
    """
    serializer_class = SavingsNumberSerializer

    def list(self, request, *args, **kwargs):
        instance = SavingsNumber.objects.latest('updated')
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class AdoptionOpportunityRecordViewSet(viewsets.ViewSet):
    @action(methods=['get'], detail=True)
    def list(self, request):
        account_uuid = request.GET.get('account_uuid', False)
        # a user can have many adoption records - one for each book
        queryset = AdoptionOpportunityRecord.objects.filter(account_uuid=account_uuid)
        book_list = []
        for record in queryset:
            book_list.append({"name": record.book_name , "students": str(max(record.students))})
        data = {"Books": book_list}

        return JsonResponse(data)


def get_adoption_status(request):
    account = request.GET.get('id', False)

    if account:
        with Salesforce() as sf:
            q = sf.query("SELECT Adoption_Status__c FROM Contact WHERE Accounts_ID__c = '{}'".format(account))

            return JsonResponse(q)
    else:
        raise Http404('Must supply account id for adoption.')
