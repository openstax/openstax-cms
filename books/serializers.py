from .models import Book
from rest_framework import serializers


class FacultyResourcesSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context['request']
        x_param = request.GET.get('x', False)
        
        book_faculty_resources = ret['book_faculty_resources']
        for resource in book_faculty_resources:
            # remove listing of linked book data
            resource['book_faculty_resource'] = {}
            #field added to API to match previous book API field
            resource['resource']['resource_unlocked'] = resource['resource']['unlocked_resource']
            # if parameter sent, clear links to faculty resources
            if x_param and x_param == 'y':
                if not resource['resource']['unlocked_resource']:
                    if resource['link_document'] is not None:
                        resource['link_document']['file'] = ''
                    if resource['link_page'] is not None:
                        resource['link_page']['url_path'] = ''
                    if resource['link_external'] is not None:
                        resource['link_external'] = ''

        book_orientation_faculty_resources = ret['book_orientation_faculty_resources']
        for resource in book_orientation_faculty_resources:
            # remove listing of linked book data
            resource['book_orientation_faculty_resource'] = {}
            # if parameter sent, clear links to faculty resources
            if x_param and x_param == 'y':
                if not resource['resource_unlocked']:
                    if resource['link_external'] is not None:
                        resource['link_external'] = ''
                    if resource['link_page'] is not None:
                        resource['link_page'] = ''
                    if resource['link_document'] is not None:
                        resource['link_document']['file'] = ''

        book_video_faculty_resources = ret['book_video_faculty_resources']
        for resource in book_video_faculty_resources:
            # remove listing of linked book data
            resource['book_video_faculty_resource'] = {}
        return ret

    class Meta:
        model = Book
        fields = ('book_video_faculty_resources','book_orientation_faculty_resources','book_faculty_resources')
        read_only_fields = ('book_video_faculty_resources','book_orientation_faculty_resources','book_faculty_resources')
        depth=2
