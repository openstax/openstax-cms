from django.core.management.base import BaseCommand
from salesforce.models import Partner, PartnerFieldNameMapping
from salesforce.salesforce import Salesforce


class Command(BaseCommand):
    help = "update partners from salesforce.com for use on the marketplace"

    def str2bool(self, v):
            if isinstance(v, bool):
                return v
            elif isinstance(v, str):
                return v.lower() == "true"
            else:
                return False

    def handle(self, *args, **options):
        with Salesforce() as sf:
            query = "SELECT " \
                    "Id, " \
                    "Name, " \
                    "Partner_Type__c, " \
                    "Books_Offered__c, " \
                    "Description, " \
                    "Rich_Description__c, " \
                    "short_partner_description__c, " \
                    "Website, " \
                    "Lead_Sharing__c, " \
                    "Verified_by_instructors__c, " \
                    "Integrated_with_OpenStax_content__c, " \
                    "Landing_page__c, " \
                    "Affordability_cost__c, " \
                    "Affordability_institutional__c, " \
                    "App_available__c, " \
                    "Adaptivity_adaptive_presentation__c, " \
                    "Adaptivity_affective_state__c, " \
                    "Adaptivity_breadth_and_depth__c, " \
                    "Adaptivity_customized_path__c, " \
                    "Adaptivity_instructor_control__c, " \
                    "Adaptivity_quantitative_randomization__c, " \
                    "Adaptivity_varied_level__c, " \
                    "Admin_calendar_links__c, " \
                    "Admin_online_submission__c, " \
                    "Admin_realtime_progress__c, " \
                    "Admin_shared_students__c, " \
                    "Admin_syllabus__c, " \
                    "Assignment_outside_resources__c, " \
                    "Assignment_editing__c, " \
                    "Assignment_multimedia__c, " \
                    "Assignment_multiple_quantitative__c, " \
                    "Assignment_pretest__c, " \
                    "Assignment_scientific_structures__c," \
                    "Assignment_summative_assessments__c, " \
                    "Autonomy_digital_badges__c, " \
                    "Autonomy_on_demand_extras__c, " \
                    "Autonomy_self_reflection__c, " \
                    "Collaboration_peer_feedback__c, " \
                    "Collaboration_peer_interaction__c, " \
                    "Collaboration_teacher_learner_contact__c, " \
                    "Collaboration_tutor__c, " \
                    "Content_batch_uploads__c, " \
                    "Content_resource_sharing__c, " \
                    "Content_sharing_among_courses__c, " \
                    "Customization_assessment_repository__c, " \
                    "Customization_create_learning_outcomes__c, " \
                    "Customization_reorder_content__c, " \
                    "Customization_reorder_learning_outcomes__c, " \
                    "Feedback_early_warning__c, " \
                    "Feedback_knowledge_gaps__c, " \
                    "Feedback_learner_progress_tasks__c, " \
                    "Feedback_multipart__c, " \
                    "Feedback_understanding__c, " \
                    "Formstack_URL__c, " \
                    "Grading_change_scores__c, " \
                    "Grading_class_and_student_level__c, " \
                    "Grading_group_work__c, " \
                    "Grading_learning_portfolio__c, " \
                    "Grading_rubric_based__c, " \
                    "Grading_tolerances_sig_fig__c, " \
                    "Interactivity_annotate__c, " \
                    "Interactivity_different_representations__c, " \
                    "Interactivity_gaming__c, " \
                    "Interactivity_previous_knowledge__c, " \
                    "Interactivity_simulations__c, " \
                    "Interactivity_varying_means__c, " \
                    "LMS_analytics__c, " \
                    "LMS_sends_grades__c, " \
                    "LMS_SSO__c, " \
                    "Measure_alternate_assessment__c, " \
                    "Measure_assessments_in_most__c, " \
                    "Measure_mapping__c, " \
                    "Reporting_competency__c, " \
                    "Reporting_student_workload__c, " \
                    "Scaffolding_hints__c, " \
                    "Scaffolding_learner_explanations__c, " \
                    "Scaffolding_mental_practice__c, " \
                    "Scaffolding_narrative__c, " \
                    "Scaffolding_social_intervention__c, " \
                    "Usability_design_orients_users__c, " \
                    "Usability_glossary__c, " \
                    "Usability_partial_progress__c, " \
                    "Accessibility_language_UI__c, " \
                    "Accessibility_language_content__c, " \
                    "Accessibility_VPAT__c, " \
                    "Accessibility_WCAG__c, " \
                    "Accessibility_Universal_Design__c, " \
                    "Instructional_level_K12__c, " \
                    "Online_teaching_peer_discussion__c, " \
                    "Online_teaching_lecture_streaming__c, " \
                    "Online_teaching_in_lecture__c, " \
                    "Online_teaching_asynchronous__c, " \
                    "Online_teaching_audio_video__c, " \
                    "Online_teaching_academic_integrity__c, " \
                    "Online_teaching_labs__c, " \
                    "International__c, " \
                    "Partnership_Level__c " \
                    "FROM Account WHERE RecordTypeId = '012U0000000MeAuIAK'"
            response = sf.query_all(query)
            sf_marketplace_partners = response['records']

            updated_partners = 0
            created_partners = 0
            partner_ids = []

            for partner in sf_marketplace_partners:
                partner_ids.append(partner['Id'])

                if partner['Affordability_cost__c']:
                    affordability_cost=partner['Affordability_cost__c'].replace(";", "; ")
                else:
                    affordability_cost=None

                p, created = Partner.objects.get_or_create(salesforce_id=partner['Id'])
                p.partner_name=partner['Name']
                p.partner_type=partner['Partner_Type__c']
                p.books=partner['Books_Offered__c']
                p.rich_description=partner['Rich_Description__c']
                p.partner_description=partner['Description']
                p.short_partner_description=partner['short_partner_description__c']
                p.partner_website=partner['Website']
                p.lead_sharing=self.str2bool(partner['Lead_Sharing__c'])
                p.landing_page=partner['Landing_page__c']
                p.verified_by_instructor=self.str2bool(partner['Verified_by_instructors__c'])
                p.integrated=partner['Integrated_with_OpenStax_content__c']
                p.affordability_cost=affordability_cost
                p.affordability_institutional=self.str2bool(partner['Affordability_Institutional__c'])
                p.app_available=self.str2bool(partner['App_available__c'])
                p.adaptivity_adaptive_presentation=self.str2bool(partner['Adaptivity_adaptive_presentation__c'])
                p.adaptivity_affective_state=self.str2bool(partner['Adaptivity_affective_state__c'])
                p.adaptivity_breadth_and_depth=self.str2bool(partner['Adaptivity_breadth_and_depth__c'])
                p.adaptivity_customized_path=self.str2bool(partner['Adaptivity_customized_path__c'])
                p.adaptivity_instructor_control=self.str2bool(partner['Adaptivity_instructor_control__c'])
                p.adaptivity_quantitative_randomization=self.str2bool(partner['Adaptivity_quantitative_randomization__c'])
                p.adaptivity_varied_level=self.str2bool(partner['Adaptivity_varied_level__c'])
                p.admin_calendar_links=self.str2bool(partner['Admin_calendar_links__c'])
                p.admin_online_submission=self.str2bool(partner['admin_online_submission__c'])
                p.admin_realtime_progress=self.str2bool(partner['Admin_realtime_progress__c'])
                p.admin_shared_students=self.str2bool(partner['Admin_shared_students__c'])
                p.admin_syllabus=self.str2bool(partner['Admin_Syllabus__c'])
                p.assigment_outside_resources=self.str2bool(partner['Assignment_outside_resources__c'])
                p.assignment_editing=self.str2bool(partner['Assignment_editing__c'])
                p.assignment_multimedia=self.str2bool(partner['Assignment_multimedia__c'])
                p.assignment_multiple_quantitative=self.str2bool(partner['Assignment_multiple_quantitative__c'])
                p.assignment_pretest=self.str2bool(partner['Assignment_pretest__c'])
                p.assignment_scientific_structures=self.str2bool(partner['Assignment_scientific_structures__c'])
                p.assignment_summative_assessments=self.str2bool(partner['Assignment_summative_assessments__c'])
                p.autonomy_digital_badges=self.str2bool(partner['Autonomy_digital_badges__c'])
                p.autonomy_on_demand_extras=self.str2bool(partner['Autonomy_on_demand_extras__c'])
                p.autonomy_self_reflection=self.str2bool(partner['Autonomy_self_reflection__c'])
                p.collaboration_peer_feedback=self.str2bool(partner['Collaboration_peer_feedback__c'])
                p.collaboration_peer_interaction=self.str2bool(partner['Collaboration_peer_interaction__c'])
                p.collaboration_teacher_learner_contact=self.str2bool(partner['Collaboration_teacher_learner_contact__c'])
                p.collaboration_tutor=self.str2bool(partner['Collaboration_tutor__c'])
                p.content_batch_uploads=self.str2bool(partner['Content_batch_uploads__c'])
                p.content_resource_sharing=self.str2bool(partner['Content_resource_sharing__c'])
                p.content_sharing_among_courses=self.str2bool(partner['Content_sharing_among_courses__c'])
                p.customization_assessement_repository=self.str2bool(partner['Customization_assessment_repository__c'])
                p.customization_create_learning_outcomes=self.str2bool(partner['Customization_create_learning_outcomes__c'])
                p.customization_reorder_content=self.str2bool(partner['Customization_reorder_content__c'])
                p.customization_reorder_learning_outcomes=self.str2bool(partner['Customization_reorder_learning_outcomes__c'])
                p.feedback_early_warning=self.str2bool(partner['Feedback_early_warning__c'])
                p.feedback_knowledge_gaps=self.str2bool(partner['Feedback_knowledge_gaps__c'])
                p.feedback_learner_progress_tasks=self.str2bool(partner['Feedback_learner_progress_tasks__c'])
                p.feedback_multipart=self.str2bool(partner['Feedback_multipart__c'])
                p.feedback_understanding=self.str2bool(partner['Feedback_understanding__c'])
                p.formstack_url=partner['Formstack_URL__c']
                p.grading_change_scores=self.str2bool(partner['Grading_change_scores__c'])
                p.grading_class_and_student_level=self.str2bool(partner['Grading_class_and_student_level__c'])
                p.grading_group_work=self.str2bool(partner['Grading_group_work__c'])
                p.grading_learning_portfolio=self.str2bool(partner['Grading_learning_portfolio__c'])
                p.grading_rubric_based=self.str2bool(partner['Grading_rubric_based__c'])
                p.grading_tolerances_sig_fig=self.str2bool(partner['Grading_tolerances_sig_fig__c'])
                p.interactivity_annotate=self.str2bool(partner['Interactivity_annotate__c'])
                p.interactivity_different_representations=self.str2bool(partner['Interactivity_different_representations__c'])
                p.interactivity_gaming=self.str2bool(partner['Interactivity_gaming__c'])
                p.interactivity_previous_knowledge=self.str2bool(partner['Interactivity_previous_knowledge__c'])
                p.interactivity_simulations=self.str2bool(partner['Interactivity_simulations__c'])
                p.interactivity_varying_means=self.str2bool(partner['Interactivity_varying_means__c'])
                p.LMS_analytics=self.str2bool(partner['LMS_analytics__c'])
                p.LMS_sends_grades=self.str2bool(partner['LMS_sends_grades__c'])
                p.LMS_SSO=self.str2bool(partner['LMS_SSO__c'])
                p.measure_alternate_assessment=self.str2bool(partner['Measure_alternate_assessment__c'])
                p.measure_assessments_in_most=self.str2bool(partner['Measure_assessments_in_most__c'])
                p.measure_mapping=self.str2bool(partner['Measure_mapping__c'])
                p.reporting_competency=self.str2bool(partner['Reporting_competency__c'])
                p.reporting_student_workload=self.str2bool(partner['Reporting_student_workload__c'])
                p.scaffolding_hints=self.str2bool(partner['Scaffolding_hints__c'])
                p.scaffolding_learner_explanations=self.str2bool(partner['Scaffolding_learner_explanations__c'])
                p.scaffolding_mental_practice=self.str2bool(partner['Scaffolding_mental_practice__c'])
                p.scaffolding_narrative=self.str2bool(partner['Scaffolding_narrative__c'])
                p.scaffolding_social_intervention=self.str2bool(partner['Scaffolding_social_intervention__c'])
                p.usability_design_orients_users=self.str2bool(partner['Usability_design_orients_users__c'])
                p.usability_glossary=self.str2bool(partner['Usability_glossary__c'])
                p.usability_partial_progress=self.str2bool(partner['Usability_partial_progress__c'])
                p.accessibility_language_UI=self.str2bool(partner['Accessibility_language_UI__c'])
                p.accessibility_language_content=self.str2bool(partner['Accessibility_language_content__c'])
                p.accessibility_VPAT=self.str2bool(partner['Accessibility_VPAT__c'])
                p.accessibility_WCAG=self.str2bool(partner['Accessibility_WCAG__c'])
                p.accessibility_universal_design=self.str2bool(partner['Accessibility_Universal_Design__c'])
                p.instructional_level_k12=self.str2bool(partner['Instructional_level_K12__c'])
                p.online_teaching_peer_discussion=self.str2bool(partner['Online_teaching_peer_discussion__c'])
                p.online_teaching_lecture_streaming=self.str2bool(partner['Online_teaching_lecture_streaming__c'])
                p.online_teaching_in_lecture=self.str2bool(partner['Online_teaching_in_lecture__c'])
                p.online_teaching_asynchronous=self.str2bool(partner['Online_teaching_asynchronous__c'])
                p.online_teaching_audio_video=self.str2bool(partner['Online_teaching_audio_video__c'])
                p.online_teaching_academic_integrity=self.str2bool(partner['Online_teaching_academic_integrity__c'])
                p.online_teaching_teaching_labs=self.str2bool(partner['Online_teaching_labs__c'])
                p.international=self.str2bool(partner['International__c'])
                p.partnership_level=partner['Partnership_Level__c']
                p.save()

                if created:
                    created_partners = created_partners + 1
                else:
                    updated_partners = updated_partners + 1

            # remove partners that have been deleted from Salesforce
            stale_partners = Partner.objects.exclude(salesforce_id__in=partner_ids)
            stale_partners.delete()

            # set Partner Field Names to hidden = true, if they are not used by any partner
            partners = Partner.objects.all()
            partner_field_names = PartnerFieldNameMapping.objects.values_list('salesforce_name', flat=True)
            hidden_field_names = PartnerFieldNameMapping.objects.values_list('salesforce_name', flat=True).filter(hidden=True)
            partner_field_names = list(partner_field_names)

            for partner in partners.iterator():
                partner_field_names = self.check_field_names(partner, partner_field_names)
                if partner_field_names is None:
                    break
            PartnerFieldNameMapping.objects.filter(salesforce_name__in=partner_field_names).update(hidden=True)
            hidden_fields_to_update = [x for x in hidden_field_names if x not in partner_field_names]
            PartnerFieldNameMapping.objects.filter(salesforce_name__in=(list(hidden_fields_to_update))).update(hidden=False)

            response = self.style.SUCCESS("Successfully updated {} partners, created {} partners.".format(updated_partners, created_partners))
        self.stdout.write(response)

    def check_field_names(self, partner, field_names):
        attributes_to_remove = []
        for attribute in field_names:
            attr_value = getattr(partner, str(attribute))
            if str(attr_value) == 'True':
                attributes_to_remove.append(attribute)
        return [x for x in field_names if x not in attributes_to_remove]
