"""Derives the partner filter menu (categories, field names, partner types)
directly from a small static registry plus live Partner data - no separate
admin-managed mapping tables to keep in sync.

To add a new filterable field: sync it from Salesforce (Partner model field +
update_partners.py's SOQL query), then add one entry under the right category
below (or a new category block). To remove a field from the filter menu,
delete its entry here; to stop syncing it entirely, also remove it from the
Partner model + SOQL query.

A field only actually appears if at least one visible Partner currently has
it set - computed live here, not stored. ``affordability_cost`` is the one
exception (ALWAYS_VISIBLE_FIELDS): it's the semicolon-delimited cost-bucket
string, not a boolean flag, and is always shown regardless of usage.
"""
from salesforce.models import Partner

ALWAYS_VISIBLE_FIELDS = {"affordability_cost"}

PARTNER_FILTER_CATEGORIES = [
    {
        "prefix": "LMS_",
        "display_name": "LMS integration",
        "fields": {
            "LMS_SSO": "Single sign-on (Lets students log in with their college account information)",
            "LMS_sends_grades": "Sends grade information to my LMS",
            "LMS_analytics": "Gives analytics back to my LMS",
        },
    },
    {
        "prefix": "interactivity_",
        "display_name": "Interactivity",
        "fields": {
            "interactivity_simulations": "Simulations that allow students to predict outcomes and analyze data",
            "interactivity_previous_knowledge": "System assesses student's previous knowledge and automatically serves follow-up questions for spaced practice",
            "interactivity_annotate": "Ability for students to highlight and annotate content",
        },
    },
    {
        "prefix": "grading_",
        "display_name": "Grading",
        "fields": {
            "grading_tolerances_sig_fig": "Ability to adjust grading tolerances; e.g., significant figure adjustments",
            "grading_rubric_based": "Ability to add scores using standards- or rubric-based grading",
            "grading_learning_portfolio": "Grading Learning Portfolio",
            "grading_group_work": "Ability for students to work and be graded as a group",
            "grading_class_and_student_level": "Analytics on both class-level and student-level competencies",
            "grading_change_scores": "Ability to change or add scores in gradebook",
        },
    },
    {
        "prefix": "feedback_",
        "display_name": "Feedback to students and instructors",
        "fields": {
            "feedback_understanding": "Ability to measure student's level of understanding",
            "feedback_multipart": "Multiple-step feedback for students",
            "feedback_learner_progress_tasks": "Feedback Learner Progress Tasks",
            "feedback_knowledge_gaps": "Students receive feedback on knowledge gaps",
            "feedback_early_warning": "Early warning system for instructors identifying students with performance issues",
        },
    },
    {
        "prefix": "assignment_",
        "display_name": "Assignment Management",
        "fields": {
            "assignment_summative_assessments": "Ability to generate, administer, and proctor summative assessments",
            "assignment_scientific_structures": "Ability to construct scientific structures (e.g., molecular drawing tools)",
            "assignment_pretest": "Offers pre-tests that give students feedback",
            "assignment_multimedia": "Ability to include multimedia content in assignments or assessments",
            "assignment_editing": "Ability to edit assignments with no coding required",
            "assignment_outside_resources": "Ability for students to upload outside resources",
        },
    },
    {
        "prefix": "adaptivity_",
        "display_name": "Adaptivity",
        "fields": {
            "adaptivity_quantitative_randomization": "System generates multiple versions of quantitative questions",
            "adaptivity_instructor_control": "Ability for instructor to control adaptivity and personalization",
            "adaptivity_customized_path": "Customized learning paths based on student input",
            "adaptivity_breadth_and_depth": "Ability to offer variation in level of content and/or depth of coverage",
            "adaptivity_adaptive_presentation": "Adaptive presentation of content based on learner goals",
        },
    },
    {
        "prefix": "app_",
        "display_name": "App Available",
        "fields": {
            "app_available": "App available",
        },
    },
    {
        "prefix": "affordability_",
        "display_name": "Cost",
        "fields": {
            "affordability_cost": "Cost per semester",
        },
    },
    {
        "prefix": "integrated",
        "display_name": "Integrated with OpenStax",
        "fields": {
            "integrated": "Integrated",
        },
    },
    {
        "prefix": "instructional_level_",
        "display_name": "Instructional Level",
        "fields": {
            "instructional_level_k12": "Supports K12",
        },
    },
    {
        "prefix": "online_teaching_",
        "display_name": "Online Teaching",
        "fields": {
            "online_teaching_peer_discussion": "Facilitates peer to peer discussion",
            "online_teaching_lecture_streaming": "Enables in-platform lecture streaming",
            "online_teaching_in_lecture": "Used actively to involve students during lecture",
            "online_teaching_asynchronous": "Used asynchronously outside of lecture",
            "online_teaching_audio_video": "Includes audio/video recording capabilities",
            "online_teaching_academic_integrity": "Contains features to ensure academic integrity in assignments",
            "online_teaching_teaching_labs": "Offers remote or virtual lab experiences",
        },
    },
    {
        "prefix": "international",
        "display_name": "International availability",
        "fields": {
            "international": "Available for users outside of the US",
        },
    },
    {
        "prefix": "accessibility_",
        "display_name": "Accessibility",
        "fields": {
            "accessibility_WCAG": "Accessibility WCAG",
            "accessibility_language_UI": "Interface available in multiple languages",
            "accessibility_language_content": "Content available in multiple languages",
            "accessibility_VPAT": "Voluntary Product Accessibility Template (VPAT) available",
            "accessibility_universal_design": "Built with universal design principles",
        },
    },
]


def _used_field_names(field_names):
    checked = [name for name in field_names if name not in ALWAYS_VISIBLE_FIELDS]
    used = {name for name in field_names if name in ALWAYS_VISIBLE_FIELDS}
    visible_partners = Partner.objects.filter(visible_on_website=True)
    if checked:
        for row in visible_partners.values(*checked):
            used.update(name for name, value in row.items() if value)
    return used


def category_mapping():
    all_field_names = [name for category in PARTNER_FILTER_CATEGORIES for name in category["fields"]]
    used = _used_field_names(all_field_names)
    return {
        category["display_name"]: category["prefix"]
        for category in PARTNER_FILTER_CATEGORIES
        if any(name in used for name in category["fields"])
    }


def field_name_mapping():
    all_field_names = [name for category in PARTNER_FILTER_CATEGORIES for name in category["fields"]]
    used = _used_field_names(all_field_names)
    result = {}
    for category in PARTNER_FILTER_CATEGORIES:
        for name, label in category["fields"].items():
            if name in used:
                result[label] = name
    return result


def partner_type_choices():
    return sorted(
        Partner.objects.filter(visible_on_website=True)
        .exclude(partner_type__isnull=True)
        .exclude(partner_type="")
        .values_list("partner_type", flat=True)
        .distinct()
    )
