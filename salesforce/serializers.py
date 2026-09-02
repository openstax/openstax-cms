from datetime import date
from collections import OrderedDict
from .models import School, AdoptionOpportunityRecord, Partner, SalesforceForms, ResourceDownload, SavingsNumber
from rest_framework import serializers


class SchoolSerializer(serializers.ModelSerializer):
    research_agreement_active = serializers.SerializerMethodField()

    def get_research_agreement_active(self, obj):
        if obj.research_agreement_start_date and obj.research_agreement_end_date:
            return obj.research_agreement_start_date <= date.today() <= obj.research_agreement_end_date
        return False

    class Meta:
        model = School
        fields = ('id',
                  'salesforce_id',
                  'name',
                  'phone',
                  'website',
                  'industry',
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
                  'lat',
                  'research_agreement_start_date',
                  'research_agreement_end_date',
                  'research_agreement_active')
        read_only_fields = ('id',
                              'salesforce_id',
                              'name',
                              'phone',
                              'website',
                              'industry',
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
                              'lat',
                              'research_agreement_start_date',
                              'research_agreement_end_date',
                              'research_agreement_active')


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
    # A reader coming back to the same thing updates that row's last access;
    # a different resource, format, or page is its own row. Source belongs in
    # the key because the same resource reached from a K12 page and from the
    # book detail page are the two facts we most need to tell apart.
    # Rows duplicated by the pre-fix behaviour are still in the table and
    # nothing constrains against them, so this takes the most recently accessed
    # match rather than get()-ing and raising.
    def create(self, validated_data):
        # An empty string and NULL both mean "not provided", and every one of
        # these is part of the key - so letting the two differ would file one
        # reader's download twice.
        for field in ('book_format', 'resource_name', 'source', 'contact_id', 'role'):
            if validated_data.get(field) == '':
                validated_data[field] = None

        existing = ResourceDownload.objects.filter(
            account_uuid=validated_data.get('account_uuid'),
            book=validated_data.get('book'),
            book_format=validated_data.get('book_format'),
            resource_name=validated_data.get('resource_name'),
            source=validated_data.get('source'),
        ).order_by('-last_access').first()

        if not existing:
            return ResourceDownload.objects.create(**validated_data)

        contact_id = validated_data.get('contact_id')
        role = validated_data.get('role')

        existing.last_access = validated_data.get('last_access', existing.last_access)
        # Signed-in students have no Salesforce contact, so an incoming
        # download without one must not erase a contact we already know.
        if contact_id:
            existing.contact_id = contact_id
        # A student who gets verified keeps the same rows; report the role they
        # hold now rather than the one they held the first time.
        if role:
            existing.role = role
        existing.save()

        return existing

    class Meta:
        model = ResourceDownload
        fields = ('id', 'book', 'book_format', 'account_uuid', 'contact_id', 'last_access', 'resource_name', 'source', 'role', 'created')
        read_only_fields = ('id', 'created', 'last_access')


class SavingsNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsNumber
        fields = ('adoptions_count', 'savings', 'updated')
        read_only_fields = ('adoptions_count', 'savings', 'updated')
