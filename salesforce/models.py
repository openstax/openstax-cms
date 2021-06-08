from django.db import models
from django.db.models import Avg
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError

from wagtail.core import hooks
from wagtail.admin.menu import MenuItem

from books.models import Book

class Adopter(models.Model):
    sales_id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True)
    website = models.URLField(max_length=255, null=True)

    def __str__(self):
        return self.name

class AdoptionOpportunityRecord(models.Model):
    opportunity_id = models.CharField(max_length=255, unique=True)
    account_id = models.CharField(max_length=255, null=True, blank=True)
    book_name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    school = models.CharField(max_length=255)
    yearly_students = models.CharField(max_length=255)
    confirmed_yearly_students = models.IntegerField(null=True, blank=True,)
    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.opportunity_id


class School(models.Model):
    salesforce_id = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    adoption_date = models.CharField(max_length=255, null=True, blank=True)
    key_institutional_partner = models.BooleanField(default=False)
    achieving_the_dream_school = models.BooleanField(default=False)
    hbcu = models.BooleanField(default=False)
    texas_higher_ed = models.BooleanField(default=False)
    undergraduate_enrollment = models.CharField(max_length=255, null=True, blank=True)
    pell_grant_recipients = models.CharField(max_length=255, null=True, blank=True)
    percent_students_pell_grant = models.CharField(max_length=255, null=True, blank=True)
    current_year_students = models.CharField(max_length=255, null=True, blank=True)
    all_time_students = models.CharField(max_length=255, null=True, blank=True)
    current_year_savings = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    all_time_savings = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    physical_country = models.CharField(max_length=255, null=True, blank=True)
    physical_street = models.CharField(max_length=255, null=True, blank=True)
    physical_city = models.CharField(max_length=255, null=True, blank=True)
    physical_state_province = models.CharField(max_length=255, null=True, blank=True)
    physical_zip_postal_code = models.CharField(max_length=255, null=True, blank=True)
    long = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    lat = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    testimonial = models.TextField(null=True, blank=True)
    testimonial_name = models.CharField(max_length=255, null=True, blank=True)
    testimonial_position = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class MapBoxDataset(models.Model):
    name = models.CharField(max_length=255)
    tileset_id = models.CharField(max_length=255)
    style_url = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if MapBoxDataset.objects.exists() and not self.pk:
            raise ValidationError('There is can be only one MapBoxDataset instance')
        return super(MapBoxDataset, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class SalesforceSettings(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    security_token = models.CharField(max_length=255)
    sandbox = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if SalesforceSettings.objects.exists() and not self.pk:
            raise ValidationError('There is can be only one SalesforceSettings instance')
        return super(SalesforceSettings, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Salesforce Settings"

class SalesforceForms(models.Model):
    oid = models.CharField(max_length=255, help_text="OID value to use for FE forms")
    posting_url = models.URLField()
    debug = models.BooleanField(default=False)

    def __str__(self):
        return self.oid

    class Meta:
        verbose_name_plural = "Salesforce Forms"

class Partner(models.Model):
    salesforce_id = models.CharField(max_length=255, blank=True, null=True)
    partner_name = models.CharField(max_length=255, blank=True, null=True)
    partner_logo = models.ImageField(upload_to='partner_logos/', null=True, blank=True)
    image_1 = models.ImageField(upload_to='partner_images/', null=True, blank=True)
    image_2 = models.ImageField(upload_to='partner_images/', null=True, blank=True)
    image_3 = models.ImageField(upload_to='partner_images/', null=True, blank=True)
    image_4 = models.ImageField(upload_to='partner_images/', null=True, blank=True)
    image_5 = models.ImageField(upload_to='partner_images/', null=True, blank=True)
    video_1 = models.FileField(upload_to='partner_videos/', null=True, blank=True)
    video_2 = models.FileField(upload_to='partner_videos/', null=True, blank=True)
    partner_list_label = models.CharField(max_length=255, null=True, blank=True)
    visible_on_website = models.BooleanField(default=False)
    lead_sharing = models.BooleanField(default=False)
    partner_type = models.CharField(max_length=255, blank=True, null=True)
    rich_description = models.TextField(blank=True, null=True)
    partner_description = models.TextField(blank=True, null=True)
    short_partner_description = models.TextField(blank=True, null=True)
    partner_website = models.CharField(max_length=255, blank=True, null=True)
    books = models.TextField(blank=True, null=True)
    landing_page = models.CharField(max_length=255, blank=True, null=True)
    verified_by_instructor = models.BooleanField(default=False)
    integrated = models.BooleanField(default=False)
    affordability_cost = models.CharField(max_length=255, blank=True, null=True)
    affordability_institutional = models.BooleanField(default=False)
    app_available = models.BooleanField(default=False)
    adaptivity_adaptive_presentation = models.BooleanField(default=False)
    adaptivity_affective_state = models.BooleanField(default=False)
    adaptivity_breadth_and_depth = models.BooleanField(default=False)
    adaptivity_customized_path = models.BooleanField(default=False)
    adaptivity_instructor_control = models.BooleanField(default=False)
    adaptivity_quantitative_randomization = models.BooleanField(default=False)
    adaptivity_varied_level = models.BooleanField(default=False)
    admin_calendar_links = models.BooleanField(default=False)
    admin_online_submission = models.BooleanField(default=False)
    admin_realtime_progress = models.BooleanField(default=False)
    admin_shared_students = models.BooleanField(default=False)
    admin_syllabus = models.BooleanField(default=False)
    assigment_outside_resources = models.BooleanField(default=False)
    assignment_editing = models.BooleanField(default=False)
    assignment_multimedia = models.BooleanField(default=False)
    assignment_multiple_quantitative = models.BooleanField(default=False)
    assignment_pretest = models.BooleanField(default=False)
    address_Longitude = models.BooleanField(default=False)
    assignment_scientific_structures = models.BooleanField(default=False)
    assignment_summative_assessments = models.BooleanField(default=False)
    autonomy_digital_badges = models.BooleanField(default=False)
    autonomy_on_demand_extras = models.BooleanField(default=False)
    autonomy_self_reflection = models.BooleanField(default=False)
    collaboration_peer_feedback = models.BooleanField(default=False)
    collaboration_peer_interaction = models.BooleanField(default=False)
    collaboration_teacher_learner_contact = models.BooleanField(default=False)
    collaboration_tutor = models.BooleanField(default=False)
    content_batch_uploads = models.BooleanField(default=False)
    content_resource_sharing = models.BooleanField(default=False)
    content_sharing_among_courses = models.BooleanField(default=False)
    customization_assessement_repository = models.BooleanField(default=False)
    customization_create_learning_outcomes = models.BooleanField(default=False)
    customization_reorder_content = models.BooleanField(default=False)
    customization_reorder_learning_outcomes = models.BooleanField(default=False)
    feedback_early_warning = models.BooleanField(default=False)
    feedback_knowledge_gaps = models.BooleanField(default=False)
    feedback_learner_progress_tasks = models.BooleanField(default=False)
    feedback_multipart = models.BooleanField(default=False)
    feedback_understanding = models.BooleanField(default=False)
    formstack_url = models.CharField(max_length=255, null=True, blank=True)
    grading_change_scores = models.BooleanField(default=False)
    grading_class_and_student_level = models.BooleanField(default=False)
    grading_group_work = models.BooleanField(default=False)
    grading_learning_portfolio = models.BooleanField(default=False)
    grading_rubric_based = models.BooleanField(default=False)
    grading_tolerances_sig_fig = models.BooleanField(default=False)
    interactivity_annotate = models.BooleanField(default=False)
    interactivity_different_representations = models.BooleanField(default=False)
    interactivity_gaming = models.BooleanField(default=False)
    interactivity_previous_knowledge = models.BooleanField(default=False)
    interactivity_simulations = models.BooleanField(default=False)
    interactivity_varying_means = models.BooleanField(default=False)
    LMS_analytics = models.BooleanField(default=False)
    LMS_sends_grades = models.BooleanField(default=False)
    LMS_SSO = models.BooleanField(default=False)
    measure_alternate_assessment = models.BooleanField(default=False)
    measure_assessments_in_most = models.BooleanField(default=False)
    measure_mapping = models.BooleanField(default=False)
    reporting_competency = models.BooleanField(default=False)
    reporting_student_workload = models.BooleanField(default=False)
    scaffolding_hints = models.BooleanField(default=False)
    scaffolding_learner_explanations = models.BooleanField(default=False)
    scaffolding_mental_practice = models.BooleanField(default=False)
    scaffolding_narrative = models.BooleanField(default=False)
    scaffolding_social_intervention = models.BooleanField(default=False)
    usability_design_orients_users = models.BooleanField(default=False)
    usability_glossary = models.BooleanField(default=False)
    usability_partial_progress = models.BooleanField(default=False)
    accessibility_language_UI = models.BooleanField(default=False)
    accessibility_language_content = models.BooleanField(default=False)
    accessibility_VPAT = models.BooleanField(default=False)
    accessibility_WCAG = models.BooleanField(default=False)
    accessibility_universal_design = models.BooleanField(default=False)
    instructional_level_k12 = models.BooleanField(default=False)
    online_teaching_peer_discussion = models.BooleanField(default=False)
    online_teaching_lecture_streaming = models.BooleanField(default=False)
    online_teaching_in_lecture = models.BooleanField(default=False)
    online_teaching_asynchronous = models.BooleanField(default=False)
    online_teaching_audio_video = models.BooleanField(default=False)
    online_teaching_academic_integrity = models.BooleanField(default=False)
    online_teaching_teaching_labs = models.BooleanField(default=False)
    international = models.BooleanField(default=False)
    partnership_level = models.CharField(max_length=255, default='', null=True)

    def __str__(self):
        return self.partner_name

    def partner_logo_tag(self):
        from django.utils.html import escape, mark_safe
        if self.partner_logo:
            return mark_safe(u'<img src="%s" height=50 />' % escape(self.partner_logo.url))
        else:
            return mark_safe(u'<img src="" />')
        image_tag.short_description = 'Image'
        image_tag.allow_tags = True

    @property
    def reviews(self):
        return list(PartnerReview.objects.filter(partner=self).values('id',
                                                                         'status',
                                                                         'rating',
                                                                         'review',
                                                                         'partner_response',
                                                                         'submitted_by_name',
                                                                         'submitted_by_account_id',
                                                                         'created',
                                                                         'updated'))

    @property
    def average_rating(self):
        return PartnerReview.objects.filter(partner=self, status='Approved').aggregate(Avg('rating'))

    @property
    def rating_count(self):
        return PartnerReview.objects.filter(partner=self, status='Approved').count()

    @hooks.register('register_admin_menu_item')
    def register_partner_menu_item():
        return MenuItem('Partners', '/django-admin/salesforce/partner/', classnames='icon icon-group', order=3000)


class PartnerFieldNameMapping(models.Model):
    salesforce_name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.display_name


class PartnerCategoryMapping(models.Model):
    salesforce_name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)

    def __str__(self):
        return self.display_name


class PartnerTypeMapping(models.Model):
    display_name = models.CharField(max_length=255)

    def __str__(self):
        return self.display_name


class PartnerReview(models.Model):
    # To track what we need to do with these re: syncing.
    # New = new to the cms (no SF ID)
    # Edited = edited by author, needs to be resynced with SF, set to NEW (SF Status) to reenter the approval queue
    STATUS_OPTIONS = (
        ('New', 'New'),
        ('Edited', 'Edited'),
        ('Awaiting Approval', 'Awaiting Approval'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Deleted', 'Deleted')
    )

    partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True)
    review_salesforce_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    rating = models.IntegerField(validators=[
            MaxValueValidator(5),
            MinValueValidator(0)
        ])
    review = models.TextField(null=True, blank=True)
    partner_response = models.TextField(null=True, blank=True)
    partner_response_date = models.DateField(null=True, blank=True)
    submitted_by_name = models.CharField(max_length=255)
    submitted_by_account_id = models.IntegerField()
    status = models.CharField(max_length=255, choices=STATUS_OPTIONS, default='New')
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.submitted_by_name


class ResourceDownload(models.Model):
    BOOK_FORMATS = (
        ('Online', 'Online'),
        ('PDF', 'PDF'),
        ('Print', 'Print'),
        ('App', 'App'),
        ('Kindle', 'Kindle'),
        ('iBooks', 'iBooks'),
        ('Bookshare', 'Bookshare'),
        ('Chegg Reader', 'Chegg Reader'),
    )
    salesforce_id = models.CharField(max_length=100, blank=True, null=True)
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True)
    book_format = models.CharField(max_length=100, choices=BOOK_FORMATS, null=True , blank=True)
    account_id = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    last_access = models.DateTimeField()
    number_of_times_accessed = models.IntegerField()
    resource_name = models.CharField(max_length=255, null=True, blank=False)
    contact_id = models.CharField(max_length=100, blank=True, default='')

    def save(self, *args, **kwargs):
        if not self.pk:
            self.number_of_times_accessed = 1
        else:
            self.number_of_times_accessed = self.number_of_times_accessed + 1
        super().save(*args, **kwargs)


    class Meta:
        indexes = [
            models.Index(fields=['account_id', ]),
            models.Index(fields=['book', ]),
        ]

class SavingsNumber(models.Model):
    adoptions_count = models.IntegerField(blank=True, null=True)
    savings = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.updated)
