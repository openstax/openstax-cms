from .models import Session

from rest_framework import serializers


class SessionSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(SessionSerializer, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].read_only = True

    class Meta:
        model = Session
        fields = '__all__'
