from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.core.exceptions import MultipleObjectsReturned

from .models import School, AdoptionOpportunityRecord, Partner, SalesforceForms, ResourceDownload, SavingsNumber, PartnerReview
from .serializers import SchoolSerializer, AdoptionOpportunityRecordSerializer, PartnerSerializer, SalesforceFormsSerializer, ResourceDownloadSerializer, SavingsNumberSerializer, PartnerReviewSerializer

from salesforce.salesforce import Salesforce
from books.models import Book
from oxauth.functions import get_logged_in_user_id
from global_settings.functions import invalidate_cloudfront_caches


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

    def perform_create(self, serializer):
        serializer.save(last_access=timezone.now())


class PartnerReviewViewSet(viewsets.ViewSet):
    @action(methods=['get'], detail=True)
    def list(self, request):
        """
        Optionally restricts the returned reviews to a given user,
        by filtering against a `user_id` query parameter in the URL.
        """
        # for a review to show up in the API, the partner should be visible and the review approved
        queryset = PartnerReview.objects.filter(partner__visible_on_website=True)
        user_id = self.request.query_params.get('user_id', None)
        if user_id is not None:
            queryset = queryset.filter(submitted_by_account_id=user_id)

        serializer = PartnerReviewSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=True)
    def post(self, request):
        try:
            try:
                review_object = PartnerReview.objects.get(partner=request.data['partner'],
                                                          submitted_by_account_id=request.data['submitted_by_account_id'])
            except MultipleObjectsReturned: # just in case they somehow were able to create more than 1
                review_object = PartnerReview.objects.filter(partner=request.data['partner'],
                                                          submitted_by_account_id=request.data[
                                                              'submitted_by_account_id']).first()
            serializer = PartnerReviewSerializer(review_object)
            return Response(serializer.data)
        except PartnerReview.DoesNotExist:
            serializer = PartnerReviewSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                invalidate_cloudfront_caches()
                return JsonResponse(status=201, data=serializer.data)
        return JsonResponse(status=400, data="wrong parameters")

    @action(methods=['patch'], detail=True)
    def patch(self, request):
        review_object = PartnerReview.objects.get(id=request.data['id'])
        serializer = PartnerReviewSerializer(review_object, data=request.data,
                                         partial=True)  # set partial=True to update a data partially
        if serializer.is_valid():
            serializer.save()
            # set review status to Edited so it will reenter the review queue
            review_object.status = 'Edited'
            review_object.save()
            invalidate_cloudfront_caches()
            return JsonResponse(status=201, data=serializer.data)
        return JsonResponse(status=400, data="wrong parameters")

    @action(method=['delete'], detail=True)
    def delete(self, request):
        user_id = get_logged_in_user_id(request)
        if user_id:
            review_object = PartnerReview.objects.get(id=request.data['id'])
            if (user_id == review_object.submitted_by_account_id) or user_id == -1:
                    review_object.status = 'Deleted'
                    review_object.save()
                    invalidate_cloudfront_caches()
            serializer = PartnerReviewSerializer(review_object)
            return Response(serializer.data)
        else:
            return Response(status=403, data="SSO cookie not set")

    serializer_class = PartnerReviewSerializer


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
    def list(self, request, account_id):
        # a user can have many adoption records - one for each book
        queryset = AdoptionOpportunityRecord.objects.filter(account_id=account_id, verified=False)
        serializer = AdoptionOpportunityRecordSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=True)
    def post(self, request, account_id, format=None):
        # this takes the adoption record as a post and looks it up, since a user can adopt more than one book
        records = AdoptionOpportunityRecord.objects.filter(account_id=account_id)
        if not records:
            return JsonResponse({'error': 'No records associated with that ID.'})

        # adoption id is included in the post request
        id = self.request.data.get('id', None)
        if id:
            try:
                record = AdoptionOpportunityRecord.objects.get(id=id)
            except AdoptionOpportunityRecord.DoesNotExist:
                return JsonResponse({'error': 'Invalid adoption id.'})

            confirmed_yearly_students = self.request.data.get('confirmed_yearly_students', 0)
            data = {"verified": True, "confirmed_yearly_students": confirmed_yearly_students}

            serializer = AdoptionOpportunityRecordSerializer(record, data=data, partial=True)

            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return JsonResponse(data)
        else:
            return JsonResponse({'error': 'Must include adoption ID to update'})


def get_adoption_status(request):
    account = request.GET.get('id', False)

    if account:
        with Salesforce() as sf:
            q = sf.query("SELECT Adoption_Status__c FROM Contact WHERE Accounts_ID__c = '{}'".format(account))

            return JsonResponse(q)
    else:
        raise Http404('Must supply account id for adoption.')
