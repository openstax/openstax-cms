from rest_framework import serializers
from .models import Webinar

class WebinarSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(WebinarSerializer, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].read_only = True

    class Meta:
        model = Webinar
        fields = '__all__'
