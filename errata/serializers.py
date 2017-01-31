from .models import Errata, ExternalDocumentation

from rest_framework import serializers

class ExternalDocumentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalDocumentation
        fields = ('file', )


class ErrataSerializer(serializers.ModelSerializer):
    external_documentation = ExternalDocumentationSerializer(many=True)
    # Read-only fields
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
                  'error_type_label',
                  'resource',
                  'resources',
                  'submitted_by',
                  'submitter_email_address',
                  'external_documentation',)
