from .models import Book
from rest_framework import serializers


class FacultyResourcesSerializer(serializers.ModelSerializer):
    # def to_representation(self, instance):
    #     ret = super().to_representation(instance)
    #     print('ret: ' + str(ret))
    #     request = self.context['request']
    #     #print('request: ' + str(request))
    #     x_param = request.GET.get('x', False)
    #     if x_param and x_param == 'y':
    #         bfr = ret['book_faculty_resources'].values()
    #         if not bfr['resource_unlocked']:
    #             bfr['link_document_url'] = ''
    #             bfr['link_external'] = ''
    #             bfr['link_page'] = ''
    #             ret['book_faculty_resources'] = bfr
    #     return ret
    class Meta:
        model = Book
        fields = ('book_video_faculty_resources','book_orientation_faculty_resources','book_faculty_resources')
        read_only_fields = ('book_video_faculty_resources','book_orientation_faculty_resources','book_faculty_resources')