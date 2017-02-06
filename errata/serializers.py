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
                  'archived',
                  'location',
                  'detail',
                  'short_detail',
                  'resolution_date',
                  'error_type',
                  'error_type_other',
                  'resource',
                  'resource_other',
                  'submitted_by',
                  'submitter_email_address',
                  'file_1',
                  'file_2')
