from .models import Book
from rest_framework import serializers


class FacultyResourcesSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context['request']
        x_param = request.GET.get('x', False)

        ret['book_faculty_resources'] = [r for r in ret['book_faculty_resources'] if not r.get('hidden')]

        book_faculty_resources = ret['book_faculty_resources']
        for resource in book_faculty_resources:
            # remove listing of linked book data
            resource['book_faculty_resource'] = {}
            # the resource snippet is SET_NULL, so a deleted snippet leaves this None
            snippet = resource['resource'] or {}
            #field added to API to match previous book API field
            snippet['resource_unlocked'] = snippet.get('unlocked_resource')
            # if parameter sent, clear links to faculty resources
            if x_param and x_param == 'y':
                if not snippet.get('unlocked_resource'):
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

        ret['book_student_resources'] = [r for r in ret['book_student_resources'] if not r.get('hidden')]

        book_student_resources = ret['book_student_resources']
        for resource in book_student_resources:
            # remove listing of linked book data
            resource['book_student_resource'] = {}
            # the resource snippet is SET_NULL, so a deleted snippet leaves this None
            snippet = resource['resource'] or {}
            # os-webview resolves student rows against the flat shape the Book
            # page API emits (StudentResources.resource_heading/_description/
            # _unlocked), not the nested `resource` dict depth=2 produces here.
            resource['resource_heading'] = snippet.get('heading')
            resource['resource_description'] = snippet.get('description')
            resource['resource_unlocked'] = snippet.get('unlocked_resource')
            # if parameter sent, clear links to locked student resources
            if x_param and x_param == 'y':
                if not snippet.get('unlocked_resource'):
                    if resource['link_document'] is not None:
                        resource['link_document']['file'] = ''
                    if resource['link_page'] is not None:
                        resource['link_page']['url_path'] = ''
                    if resource['link_external'] is not None:
                        resource['link_external'] = ''
        return ret

    class Meta:
        model = Book
        fields = ('book_video_faculty_resources','book_orientation_faculty_resources','book_faculty_resources',
                  'audiobook_link','book_student_resources')
        read_only_fields = ('book_video_faculty_resources','book_orientation_faculty_resources','book_faculty_resources',
                            'audiobook_link','book_student_resources')
        depth=2
