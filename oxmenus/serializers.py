from rest_framework import serializers
from .models import Menus


class OXMenusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Menus
        fields = ('name',
                  'menu')
        read_only_fields = ('name',
                            'menu')