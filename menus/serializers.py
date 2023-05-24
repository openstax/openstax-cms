from rest_framework import serializers
from .models import Menus


class MenusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menus
        fields = ('id',
                  'menu')
        read_only_fields = ('id',
                            'menu')