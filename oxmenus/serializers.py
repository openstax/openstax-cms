from rest_framework import serializers
from .models import Menus


class OXMenusSerializer(serializers.ModelSerializer):
    menu = serializers.SerializerMethodField()

    def get_menu(self, obj):
        return obj.menu_block_json()


    class Meta:
        model = Menus
        fields = ('name',
                  'menu')
        read_only_fields = ('name',
                            'menu')
