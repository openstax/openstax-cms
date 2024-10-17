from collections import OrderedDict
from .models import School, AdoptionOpportunityRecord, Partner, SalesforceForms, ResourceDownload, SavingsNumber
from rest_framework import serializers


class SchoolSerializer(serializers.ModelSerializer):

    class Meta:
        model = School
        fields = ('id',
                  'name',
                  'phone',
                  'website',
                  'type',
                  'location',
                  'adoption_date',
                  'key_institutional_partner',
                  'achieving_the_dream_school',
                  'hbcu',
                  'texas_higher_ed',
                  'undergraduate_enrollment',
                  'pell_grant_recipients',
                  'percent_students_pell_grant',
                  'current_year_students',
                  'all_time_students',
                  'total_school_enrollment',
                  'current_year_savings',
                  'all_time_savings',
                  'physical_country',
                  'physical_street',
                  'physical_city',
                  'physical_state_province',
                  'physical_zip_postal_code',
                  'long',
                  'lat')
        read_only_fields = ('id',
                              'name',
                              'phone',
                              'website',
                              'type',
                              'location',
                              'adoption_date',
                              'key_institutional_partner',
                              'achieving_the_dream_school',
                              'hbcu',
                              'texas_higher_ed',
                              'undergraduate_enrollment',
                              'pell_grant_recipients',
                              'percent_students_pell_grant',
                              'current_year_students',
                              'all_time_students',
                              'total_school_enrollment',
                              'current_year_savings',
                              'all_time_savings',
                              'physical_country',
                              'physical_street',
                              'physical_city',
                              'physical_state_province',
                              'physical_zip_postal_code',
                              'long',
                              'lat')


class AdoptionOpportunityRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdoptionOpportunityRecord
        fields = ('id',
                  'opportunity_id',
                  'account_uuid',
                  'book_name',
                  'created')
        read_only_fields = ('id',
                  'opportunity_id',
                  'account_uuid',
                  'book_name',
                  'created',
                  )

class PartnerSerializer(serializers.ModelSerializer):
    # TODO: remove
    reviews = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    rating_count = serializers.ReadOnlyField()

    def __init__(self, *args, **kwargs):
        super(PartnerSerializer, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].read_only = True

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        # TODO: remove
        # if looking at an individual partner instance, include the reviews - else, exclude
        if not isinstance(self.instance, Partner):
            ret['reviews'] = False

        # Here we filter the null values and creates a new dictionary
        # We use OrderedDict like in original method
        ret = OrderedDict(filter(lambda x: x[1] is not False, ret.items()))
        return ret

    class Meta:
        model = Partner
        fields = '__all__'


class SalesforceFormsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesforceForms
        fields = ('oid', 'debug', 'debug_email', 'posting_url', 'adoption_form_posting_url', 'interest_form_posting_url', 'tech_scout_form_posting_url')
        read_only_fields = ('oid', 'debug', 'debug_email', 'posting_url', 'adoption_form_posting_url', 'interest_form_posting_url', 'tech_scout_form_posting_url')


class ResourceDownloadSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        book = validated_data.get('book', None)
        book_format = validated_data.get('book_format', None)
        account_uuid = validated_data.get('account_uuid', None)
        resource_name = validated_data.get('resource_name', None)
        contact_id = validated_data.get('contact_id', None)
        rd = []
        try:
            rd = ResourceDownload.objects.filter(account_uuid=account_uuid, book=book)
            if resource_name:
                rd.filter(resource_name=resource_name)

            rd = rd[0]
            rd.contact_id = contact_id
            rd.save()
        except (ResourceDownload.DoesNotExist, IndexError):
            rd = ResourceDownload.objects.create(**validated_data)

        return rd

    class Meta:
        model = ResourceDownload
        fields = ('id', 'book', 'book_format', 'account_uuid', 'contact_id', 'last_access', 'resource_name', 'created')
        read_only_fields = ('id', 'created', 'last_access', 'number_of_times_accessed')


class SavingsNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsNumber
        fields = ('adoptions_count', 'savings', 'updated')
        read_only_fields = ('adoptions_count', 'savings', 'updated')
