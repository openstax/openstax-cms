from rest_framework import serializers
from .models import Menus


class OXMenusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menus
        fields = ('name', 'key', 'feature_flag', 'flag_value', 'partial_url', 'menu',
                  'region', 'component_key')
        read_only_fields = fields

    def to_representation(self, obj):
        node_type = obj.node_type()
        common = {
            'region': obj.region,
            'key': obj.key,
            'feature_flag': obj.feature_flag,
            'flag_value': obj.flag_value,
        }
        if node_type == 'dynamic':
            return {**common, 'type': 'dynamic',
                    'component': obj.component_key, 'label': obj.name}
        if node_type == 'link':
            return {**common, 'type': 'link',
                    'label': obj.name, 'partial_url': obj.partial_url}
        return {**common, 'type': 'dropdown',
                'name': obj.name, 'menu': obj.menu_block_json()}
