from .models import School

from rest_framework import serializers

from django.utils.formats import number_format
import locale

class SchoolSerializer(serializers.ModelSerializer):
    all_time_savings = serializers.SerializerMethodField('all_time_savings_localize')
    current_year_savings = serializers.SerializerMethodField('current_year_savings_localize')

    class Meta:
        model = School
        fields = ('id',
                  'name',
                  'phone',
                  'website',
                  'type',
                  'adoption_date',
                  'key_institutional_partner',
                  'achieving_the_dream_school',
                  'hbcu',
                  'texas_higher_ed',
                  'undergraduate_enrollment',
                  'pell_grant_recipients',
                  'percent_students_pell_grant',
                  'current_year_students',
                  'all_time_students',
                  'current_year_savings',
                  'all_time_savings',
                  'physical_country',
                  'physical_street',
                  'physical_city',
                  'physical_state_province',
                  'physical_zip_postal_code',
                  'long',
                  'lat',
                  'testimonial',)

    def all_time_savings_localize(self, obj):
        locale.setlocale(locale.LC_ALL, 'en_US')
        return locale.format("%d", int(obj.all_time_savings), grouping=True)


    def current_year_savings_localize(self, obj):
        locale.setlocale(locale.LC_ALL, 'en_US')
        return locale.format("%d", int(obj.current_year_savings), grouping=True)
