from django.contrib import admin
from django.core import management

from .models import AdoptionOpportunityRecord, \
    School, \
    MapBoxDataset, \
    SalesforceSettings, \
    SalesforceForms, \
    Partner, \
    PartnerCategoryMapping, \
    PartnerFieldNameMapping, \
    PartnerTypeMapping, \
    PartnerReview, \
    ResourceDownload, \
    SavingsNumber


class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone']
    list_filter = ('key_institutional_partner', 'achieving_the_dream_school', 'hbcu', 'texas_higher_ed')
    search_fields = ['name', ]

    def has_add_permission(self, request):
        return False

class AdoptionOpportunityRecordAdmin(admin.ModelAdmin):
    list_display = ['email', 'book_name', 'school', 'yearly_students', 'verified']
    list_filter = ('book_name', 'school', 'verified', 'last_update')
    search_fields = ['email', 'account_id']

    def has_add_permission(self, request):
        return False


class SalesforceSettingsAdmin(admin.ModelAdmin):
    # only allow one SF Setting to exist
    def has_add_permission(self, request):
        num_objects = self.model.objects.count()
        if num_objects >= 1:
            return False
        else:
            return True


class SalesforceFormsAdmin(admin.ModelAdmin):
    # only allow one SF Setting to exist
    def has_add_permission(self, request):
        num_objects = self.model.objects.count()
        if num_objects >= 1:
            return False
        else:
            return True


class PartnerAdmin(admin.ModelAdmin):
    list_display = ['partner_logo_tag', 'salesforce_id', 'partner_name', 'partner_type', 'visible_on_website', 'lead_sharing']
    list_display_links = ('partner_name', )
    list_filter = ('visible_on_website', 'partner_type')
    search_fields = ('partner_name', 'salesforce_id')
    readonly_fields = (
        'salesforce_id',
    'partner_name',
    'partner_type',
    'rich_description',
    'partner_description',
    'partner_website',
    'short_partner_description',
    'books',
    'lead_sharing',
    'landing_page',
    'verified_by_instructor',
    'integrated',
    'affordability_cost',
    'affordability_institutional',
    'app_available',
    'adaptivity_adaptive_presentation',
    'adaptivity_affective_state',
    'adaptivity_breadth_and_depth',
    'adaptivity_customized_path',
    'adaptivity_instructor_control',
    'adaptivity_quantitative_randomization',
    'adaptivity_varied_level',
    'admin_calendar_links',
    'admin_online_submission',
    'admin_realtime_progress',
    'admin_shared_students',
    'admin_syllabus',
    'assigment_outside_resources',
    'assignment_editing',
    'assignment_multimedia',
    'assignment_multiple_quantitative',
    'assignment_pretest',
    'address_Longitude',
    'assignment_scientific_structures',
    'assignment_summative_assessments',
    'autonomy_digital_badges',
    'autonomy_on_demand_extras',
    'autonomy_self_reflection',
    'collaboration_peer_feedback',
    'collaboration_peer_interaction',
    'collaboration_teacher_learner_contact',
    'collaboration_tutor',
    'content_batch_uploads',
    'content_resource_sharing',
    'content_sharing_among_courses',
    'customization_assessement_repository',
    'customization_create_learning_outcomes',
    'customization_reorder_content',
    'customization_reorder_learning_outcomes',
    'feedback_early_warning',
    'feedback_knowledge_gaps',
    'feedback_learner_progress_tasks',
    'feedback_multipart',
    'feedback_understanding',
    'formstack_url',
    'grading_change_scores',
    'grading_class_and_student_level',
    'grading_group_work',
    'grading_learning_portfolio',
    'grading_rubric_based',
    'grading_tolerances_sig_fig',
    'interactivity_annotate',
    'interactivity_different_representations',
    'interactivity_gaming',
    'interactivity_previous_knowledge',
    'interactivity_simulations',
    'interactivity_varying_means',
    'instructional_level_k12',
    'LMS_analytics',
    'LMS_sends_grades',
    'LMS_SSO',
    'measure_alternate_assessment',
    'measure_assessments_in_most',
    'measure_mapping',
    'reporting_competency',
    'reporting_student_workload',
    'scaffolding_hints',
    'scaffolding_learner_explanations',
    'scaffolding_mental_practice',
    'scaffolding_narrative',
    'scaffolding_social_intervention',
    'usability_design_orients_users',
    'usability_glossary',
    'usability_partial_progress',
    'accessibility_language_UI',
    'accessibility_language_content',
    'accessibility_VPAT',
    'accessibility_WCAG',
    'accessibility_universal_design',
    'partner_logo_tag',
    'online_teaching_peer_discussion',
    'online_teaching_lecture_streaming',
    'online_teaching_in_lecture',
    'online_teaching_asynchronous',
    'online_teaching_audio_video',
    'online_teaching_academic_integrity',
    'online_teaching_teaching_labs',
    'international',
    'partnership_level')

    actions = ['sync_with_salesforce', 'mark_visible', 'mark_not_visible' ]

    def sync_with_salesforce(self, request, queryset):
        management.call_command('update_partners', verbosity=0)
    sync_with_salesforce.short_description = "Sync Partners with Salesforce"
    sync_with_salesforce.allowed_permissions = ('change',)

    def mark_visible(self, request, queryset):
        queryset.update(visible_on_website=True)
    mark_visible.short_description = "Mark partners as visible on website"
    mark_visible.allowed_permissions = ('change',)

    def mark_not_visible(self, request, queryset):
        queryset.update(visible_on_website=False)
    mark_not_visible.short_description = "Mark partners as not visible on website"
    mark_not_visible.allowed_permissions = ('change',)

class PartnerCategoryMappingAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'salesforce_name')


class PartnerFieldNameMappingAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'salesforce_name')


class PartnerTypeMappingAdmin(admin.ModelAdmin):
    list_display = ('display_name',)


class PartnerReviewAdmin(admin.ModelAdmin):
    list_display = ('partner', 'submitted_by_name', 'rating', 'status')
    list_filter = ('rating', 'partner')
    search_fields = ['partner', 'submitted_by_name', 'submitted_by_account_id']
    actions = ['sync_with_salesforce', ]

    def sync_with_salesforce(self, request, queryset):
        management.call_command('sync_reviews', verbosity=0)
    sync_with_salesforce.short_description = "Sync Reviews with Salesforce"
    sync_with_salesforce.allowed_permissions = ('change',)


class ResourceDownloadAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'last_access', 'salesforce_id', 'resource_name', 'book', 'book_format', 'account_id', 'number_of_times_accessed')
    list_filter = ('created', 'book')

admin.site.register(SalesforceSettings, SalesforceSettingsAdmin)
admin.site.register(SalesforceForms, SalesforceFormsAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(AdoptionOpportunityRecord, AdoptionOpportunityRecordAdmin)
admin.site.register(MapBoxDataset)
admin.site.register(Partner, PartnerAdmin)
admin.site.register(PartnerCategoryMapping, PartnerCategoryMappingAdmin)
admin.site.register(PartnerFieldNameMapping, PartnerFieldNameMappingAdmin)
admin.site.register(PartnerTypeMapping, PartnerTypeMappingAdmin)
admin.site.register(PartnerReview, PartnerReviewAdmin)
admin.site.register(ResourceDownload, ResourceDownloadAdmin)
admin.site.register(SavingsNumber)
