from .models import Session, Registration
from .functions import check_eventbrite_registration

from rest_framework import serializers


class SessionSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(SessionSerializer, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].read_only = True

    class Meta:
        model = Session
        fields = '__all__'


class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Registration
        fields = ('session', 'first_name', 'last_name', 'registration_email')

    def validate(self, data):
        if check_eventbrite_registration(data['registration_email']):
            try:
                Registration.objects.get(registration_email=data['registration_email'])
                raise serializers.ValidationError("You can only register for one session.")
            except Registration.DoesNotExist:
                return data
        else:
            raise serializers.ValidationError("Email address not registered for event.")

    def create(self, validated_data):
        registration_instance = Registration.objects.create(**validated_data)
        return registration_instance

