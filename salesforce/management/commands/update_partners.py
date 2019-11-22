from pprint import pprint
from django.core.management.base import BaseCommand
from salesforce.models import Partner
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
                    "short_partner_description__c, " \
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
                    "Accessibility_Universal_Design__c " \
                    "FROM Account WHERE RecordTypeId = '012U0000000MeAuIAK'"
            response = sf.query_all(query)
            sf_marketplace_partners = response['records']

            updated_partners = 0
            created_partners = 0
            pprint(sf_marketplace_partners[3])
            for partner in sf_marketplace_partners:
                partner, created = Partner.objects.update_or_create(
                        salesforce_id=partner['Id'],
                        defaults={'partner_name': partner['Name'],
                                  'partner_type': partner['Partner_Type__c'],
                                  'books': partner['Books_Offered__c'],
                                  'partner_description': partner['Description'],
                                  'short_partner_description': partner['Short_Partner_Description__c'],
                                  'landing_page': partner['Landing_page__c'],
                                  'verified_by_instructor': partner['Verified_by_instructors__c'],
                                  'integrated': partner['Integrated_with_OpenStax_content__c'],
                                  'affordability_cost': self.str2bool(partner['Affordability_cost__c']),
                                  'affordability_institutional': self.str2bool(partner['Affordability_Institutional__c']),
                                  'app_available': self.str2bool(partner['App_available__c']),
                                  'adaptivity_adaptive_presentation': self.str2bool(partner['Adaptivity_adaptive_presentation__c']),
                                  'adaptivity_affective_state': self.str2bool(partner['Adaptivity_affective_state__c']),
                                  'adaptivity_breadth_and_depth': self.str2bool(partner['Adaptivity_breadth_and_depth__c']),
                                  'adaptivity_customized_path': self.str2bool(partner['Adaptivity_customized_path__c']),
                                  'adaptivity_instructor_control': self.str2bool(partner['Adaptivity_instructor_control__c']),
                                  'adaptivity_quantitative_randomization': self.str2bool(partner['Adaptivity_quantitative_randomization__c']),
                                  'adaptivity_varied_level': self.str2bool(partner['Adaptivity_varied_level__c']),
                                  'admin_calendar_links': self.str2bool(partner['Admin_calendar_links__c']),
                                  'admin_online_submission': self.str2bool(partner['admin_online_submission__c']),
                                  'admin_realtime_progress': self.str2bool(partner['Admin_realtime_progress__c']),
                                  'admin_shared_students': self.str2bool(partner['Admin_shared_students__c']),
                                  'admin_syllabus': self.str2bool(partner['Admin_Syllabus__c']),
                                  'assigment_outside_resources': self.str2bool(partner['Assignment_outside_resources__c']),
                                  'assignment_editing': self.str2bool(partner['Assignment_editing__c']),
                                  'assignment_multimedia': self.str2bool(partner['Assignment_multimedia__c']),
                                  'assignment_multiple_quantitative': self.str2bool(partner['Assignment_multiple_quantitative__c']),
                                  'assignment_pretest': self.str2bool(partner['Assignment_pretest__c']),
                                  'assignment_scientific_structures': self.str2bool(partner['Assignment_scientific_structures__c']),
                                  'assignment_summative_assessments': self.str2bool(partner['Assignment_summative_assessments__c']),
                                  'autonomy_digital_badges': self.str2bool(partner['Autonomy_digital_badges__c']),
                                  'autonomy_on_demand_extras': self.str2bool(partner['Autonomy_on_demand_extras__c']),
                                  'autonomy_self_reflection': self.str2bool(partner['Autonomy_self_reflection__c']),
                                  'collaboration_peer_feedback': self.str2bool(partner['Collaboration_peer_feedback__c']),
                                  'collaboration_peer_interaction': self.str2bool(partner['Collaboration_peer_interaction__c']),
                                  'collaboration_teacher_learner_contact': self.str2bool(partner['Collaboration_teacher_learner_contact__c']),
                                  'collaboration_tutor': self.str2bool(partner['Collaboration_tutor__c']),
                                  'content_batch_uploads': self.str2bool(partner['Content_batch_uploads__c']),
                                  'content_resource_sharing': self.str2bool(partner['Content_resource_sharing__c']),
                                  'content_sharing_among_courses': self.str2bool(partner['Content_sharing_among_courses__c']),
                                  'customization_assessement_repository': self.str2bool(partner['Customization_assessment_repository__c']),
                                  'customization_create_learning_outcomes': self.str2bool(partner['Customization_create_learning_outcomes__c']),
                                  'customization_reorder_content': self.str2bool(partner['Customization_reorder_content__c']),
                                  'customization_reorder_learning_outcomes': self.str2bool(partner['Customization_reorder_learning_outcomes__c']),
                                  'feedback_early_warning': self.str2bool(partner['Feedback_early_warning__c']),
                                  'feedback_knowledge_gaps': self.str2bool(partner['Feedback_knowledge_gaps__c']),
                                  'feedback_learner_progress_tasks': self.str2bool(partner['Feedback_learner_progress_tasks__c']),
                                  'feedback_multipart': self.str2bool(partner['Feedback_multipart__c']),
                                  'feedback_understanding': self.str2bool(partner['Feedback_understanding__c']),
                                  'grading_change_scores': self.str2bool(partner['Grading_change_scores__c']),
                                  'grading_class_and_student_level': self.str2bool(partner['Grading_class_and_student_level__c']),
                                  'grading_group_work': self.str2bool(partner['Grading_group_work__c']),
                                  'grading_learning_portfolio': self.str2bool(partner['Grading_learning_portfolio__c']),
                                  'grading_rubric_based': self.str2bool(partner['Grading_rubric_based__c']),
                                  'grading_tolerances_sig_fig': self.str2bool(partner['Grading_tolerances_sig_fig__c']),
                                  'interactivity_annotate': self.str2bool(partner['Interactivity_annotate__c']),
                                  'interactivity_different_representations': self.str2bool(partner['Interactivity_different_representations__c']),
                                  'interactivity_gaming': self.str2bool(partner['Interactivity_gaming__c']),
                                  'interactivity_previous_knowledge': self.str2bool(partner['Interactivity_previous_knowledge__c']),
                                  'interactivity_simulations': self.str2bool(partner['Interactivity_simulations__c']),
                                  'interactivity_varying_means': self.str2bool(partner['Interactivity_varying_means__c']),
                                  'LMS_analytics': self.str2bool(partner['LMS_analytics__c']),
                                  'LMS_sends_grades': self.str2bool(partner['LMS_sends_grades__c']),
                                  'LMS_SSO': self.str2bool(partner['LMS_SSO__c']),
                                  'measure_alternate_assessment': self.str2bool(partner['Measure_alternate_assessment__c']),
                                  'measure_assessments_in_most': self.str2bool(partner['Measure_assessments_in_most__c']),
                                  'measure_mapping': self.str2bool(partner['Measure_mapping__c']),
                                  'reporting_competency': self.str2bool(partner['Reporting_competency__c']),
                                  'reporting_student_workload': self.str2bool(partner['Reporting_student_workload__c']),
                                  'scaffolding_hints': self.str2bool(partner['Scaffolding_hints__c']),
                                  'scaffolding_learner_explanations': self.str2bool(partner['Scaffolding_learner_explanations__c']),
                                  'scaffolding_mental_practice': self.str2bool(partner['Scaffolding_mental_practice__c']),
                                  'scaffolding_narrative': self.str2bool(partner['Scaffolding_narrative__c']),
                                  'scaffolding_social_intervention': self.str2bool(partner['Scaffolding_social_intervention__c']),
                                  'usability_design_orients_users': self.str2bool(partner['Usability_design_orients_users__c']),
                                  'usability_glossary': self.str2bool(partner['Usability_glossary__c']),
                                  'usability_partial_progress': self.str2bool(partner['Usability_partial_progress__c']),
                                  'accessibility_language_UI': self.str2bool(partner['Accessibility_language_UI__c']),
                                  'accessibility_language_content': self.str2bool(partner['Accessibility_language_content__c']),
                                  'accessibility_VPAT': self.str2bool(partner['Accessibility_VPAT__c']),
                                  'accessibility_WCAG': self.str2bool(partner['Accessibility_WCAG__c']),
                                  'accessibility_universal_design': self.str2bool(partner['Accessibility_Universal_Design__c']),
                                  },
                    )
                partner.save()
                if created:
                    created_partners = created_partners + 1
                else:
                    updated_partners = updated_partners + 1



            response = self.style.SUCCESS("Successfully updated {} partners, created {} partners.".format(updated_partners, created_partners))
        self.stdout.write(response)
