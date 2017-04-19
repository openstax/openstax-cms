from .models import Errata

from rest_framework import serializers


class ErrataSerializer(serializers.ModelSerializer):
    resolution_date = serializers.DateField(read_only=True)

    class Meta:
        model = Errata
        fields = ('id',
                  'created',
                  'modified',
                  'book',
                  'status',
                  'resolution',
                  'reviewed_date',
                  'corrected_date',
                  'archived',
                  'location',
                  'detail',
                  'short_detail',
                  'resolution_date',
                  'resolution_notes',
                  'error_type',
                  'error_type_other',
                  'resource',
                  'resource_other',
                  'submitted_by',
                  'submitter_email_address',
                  'file_1',
                  'file_2')
