from rest_framework import serializers
from .models import Menus


class OXMenusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menus
        fields = ('name', 'key', 'feature_flag', 'flag_value', 'partial_url', 'menu')
        read_only_fields = fields

    def to_representation(self, obj):
        common = {
            'key': obj.key,
            'feature_flag': obj.feature_flag,
            'flag_value': obj.flag_value,
        }
        if obj.partial_url:
            # Standalone top-level link, not a dropdown.
            return {**common, 'label': obj.name, 'partial_url': obj.partial_url}
        return {**common, 'name': obj.name, 'menu': obj.menu_block_json()}
