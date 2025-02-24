from django.db import models
from django.core.exceptions import ValidationError
from wagtail.search import index
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import TranslatableMixin
from wagtail.snippets.models import register_snippet
from openstax.functions import build_image_url
from books.constants import BOOK_STATES, COVER_COLORS, K12_CATEGORIES


class Subject(TranslatableMixin, models.Model):
    name = models.CharField(max_length=255)
    page_content = models.TextField(blank=True, help_text="Content that appears on the subjects page when looking at a subject.")
    seo_title = models.CharField(max_length=255, null=True, blank=True)
    search_description = models.CharField(max_length=255, null=True, blank=True)
    icon = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    subject_color = models.CharField(max_length=255, choices=COVER_COLORS, default='blue',
                                   help_text='The color of the vertical stripe on Subject page.')

    def get_subject_icon(self):
        return build_image_url(self.icon)

    subject_icon = property(get_subject_icon)

    api_fields = ('name', 'page_content', 'seo_title', 'search_description', 'subject_icon', 'subject_color')

    panels = [
        FieldPanel('name'),
        FieldPanel('page_content'),
        FieldPanel('seo_title'),
        FieldPanel('search_description'),
        FieldPanel('icon'),
        FieldPanel('subject_color'),
    ]

    def __str__(self):
        return self.name


register_snippet(Subject)

class K12Subject(TranslatableMixin, models.Model):
    name = models.CharField(max_length=255)
    intro_text = RichTextField(blank=True, null=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    subject_category = models.CharField(max_length=255, choices=K12_CATEGORIES, default='None',
                                   help_text='The category used in the K12 subjects listings')
    subject_color = models.CharField(max_length=255, choices=COVER_COLORS, default='blue',
                                   help_text='The color of the vertical stripe on Subject page.')
    subject_link = models.CharField(max_length=255, null=True, blank=True)

    def get_subject_image(self):
        return build_image_url(self.image)

    subject_image = property(get_subject_image)

    api_fields = ('name', 'intro_text', 'subject_image', 'subject_category' , 'subject_color', 'subject_link')

    panels = [
        FieldPanel('name'),
        FieldPanel('intro_text'),
        FieldPanel('image'),
        FieldPanel('subject_category'),
        FieldPanel('subject_color'),
        FieldPanel('subject_link'),
    ]

    def __str__(self):
        return self.name

register_snippet(K12Subject)

class FacultyResource(TranslatableMixin, index.Indexed, models.Model):
    heading = models.CharField(max_length=255)
    description = RichTextField(blank=True, null=True)
    unlocked_resource = models.BooleanField(default=False)
    creator_fest_resource = models.BooleanField(default=False)
    icon = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text = 'icon used on K12 Subject pages'
    )
    resource_category = models.CharField(max_length=255, blank=True, null=True, help_text="Category for GA4")

    def get_resource_icon(self):
        return build_image_url(self.icon)

    resource_icon = property(get_resource_icon)

    api_fields = ('heading', 'description', 'unlocked_resource', 'creator_fest_resource',  'resource_icon', 'resource_category')

    panels = [
        FieldPanel('heading'),
        FieldPanel('description'),
        FieldPanel('unlocked_resource'),
        FieldPanel('creator_fest_resource'),
        FieldPanel('icon'),
        FieldPanel('resource_category')
    ]

    search_fields = [
        index.SearchField('heading', boost=10),
        index.AutocompleteField('heading'),
        index.FilterField('heading'),
        index.FilterField('locale_id'),
    ]

    def __str__(self):
        return self.heading


register_snippet(FacultyResource)


class StudentResource(TranslatableMixin, index.Indexed, models.Model):
    heading = models.CharField(max_length=255)
    description = RichTextField(blank=True, null=True)
    unlocked_resource = models.BooleanField(default=True)
    icon = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text = 'icon used on K12 Subject pages'
    )
    resource_category = models.CharField(max_length=255, blank=True, null=True, help_text="Category for GA4")
    def get_resource_icon(self):
        return build_image_url(self.icon)

    resource_icon = property(get_resource_icon)

    api_fields = ('heading', 'description', 'unlocked_resource', 'resource_icon', 'resource_category')

    panels = [
        FieldPanel('heading'),
        FieldPanel('description'),
        FieldPanel('unlocked_resource'),
        FieldPanel('icon'),
        FieldPanel('resource_category')
    ]

    search_fields = [
        index.SearchField('heading', boost=10),
        index.AutocompleteField('heading'),
        index.FilterField('heading'),
        index.FilterField('locale_id'),
    ]

    def __str__(self):
        return self.heading


register_snippet(StudentResource)


class Role(TranslatableMixin, models.Model):
    display_name = models.CharField(max_length=255)
    salesforce_name = models.CharField(max_length=255)

    api_fields = ('display_name',
                  'salesforce_name')

    panels = [
        FieldPanel('display_name'),
        FieldPanel('salesforce_name'),
    ]

    def __str__(self):
        return self.display_name


register_snippet(Role)


class SharedContent(TranslatableMixin, index.Indexed, models.Model):
    title = models.CharField(max_length=255, help_text="Internal name for identification.")
    heading = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    content_logged_in = models.TextField(null=True, blank=True)
    button_text = models.CharField(max_length=255, null=True, blank=True)
    button_url = models.URLField(null=True, blank=True)

    api_fields = ('heading', 'content', 'content_logged_in', 'button_text', 'button_url' )

    panels = [
        FieldPanel('title'),
        FieldPanel('heading'),
        FieldPanel('content'),
        FieldPanel('content_logged_in'),
        FieldPanel('button_text'),
        FieldPanel('button_url'),
    ]

    search_fields = [
        index.SearchField('title', boost=10),
        index.AutocompleteField('title'),
        index.FilterField('title'),
    ]

    def __str__(self):
        return self.title


register_snippet(SharedContent)


class NewsSource(TranslatableMixin, index.Indexed, models.Model):
    name = models.CharField(max_length=255)
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    def get_news_logo(self):
        return build_image_url(self.logo)

    news_logo = property(get_news_logo)

    api_fields = ('name', 'news_logo',)

    panels = [
        FieldPanel('name'),
        FieldPanel('logo'),
    ]

    search_fields = [
        index.SearchField('name', boost=10),
        index.AutocompleteField('name'),
        index.FilterField('name'),
        index.FilterField('locale_id')
    ]

    def __str__(self):
        return self.name


register_snippet(NewsSource)


class ErrataContent(TranslatableMixin, index.Indexed, models.Model):
    heading = models.CharField(max_length=255, blank=True, null=True)
    book_state = models.CharField(max_length=255, choices=BOOK_STATES, default='live', help_text='The state of the book.')
    content = models.TextField()

    panels = [
        FieldPanel('heading'),
        FieldPanel('book_state'),
        FieldPanel('content')
    ]

    api_fields = ('heading', 'book_state', 'content')

    def __str__(self):
        return self.heading


register_snippet(ErrataContent)


class SubjectCategory(TranslatableMixin, models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, related_name='+')
    subject_category = models.CharField(max_length=255, null=True, blank=True, help_text="category for selected subject.")
    description = models.TextField(default='')

    @property
    def subject_name(self):
        return self.subject.name

    panels = [
        FieldPanel('subject'),
        FieldPanel('subject_category'),
        FieldPanel('description'),
    ]

    api_fields = ('subject_name', 'subject_category', 'description')

    def __str__(self):
        return self.subject_category + ' - ' + self.subject_name


register_snippet(SubjectCategory)


class GiveBanner(TranslatableMixin, models.Model):
    html_message = models.TextField(default='')
    link_text = models.CharField(max_length=255, null=True, blank=True)
    link_url = models.URLField(null=True, blank=True)
    thumbnail = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_banner_thumbnail(self):
        return build_image_url(self.thumbnail)

    banner_thumbnail = property(get_banner_thumbnail)

    api_fields = ('html_message', 'link_text', 'link_url', 'banner_thumbnail')

    panels = [
        FieldPanel('html_message'),
        FieldPanel('link_text'),
        FieldPanel('link_url'),
        FieldPanel('thumbnail'),
    ]

    def __str__(self):
        return 'Give Banner'

    def clean(self):
        if GiveBanner.objects.exists() and not self.pk:
            raise ValidationError('There can be only one Give Banner instance')

    def save(self, *args, **kwargs):
        self.clean()
        return super(GiveBanner, self).save(*args, **kwargs)


register_snippet(GiveBanner)


class BlogContentType(TranslatableMixin, models.Model):
    content_type = models.CharField(max_length=255, null=True, blank=True,help_text="content type for blog posts")

    api_fields = ('content_type')

    panels = [
        FieldPanel('content_type'),
    ]

    def __str__(self):
        return self.content_type


register_snippet(BlogContentType)


class BlogCollection(TranslatableMixin, models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(default='')
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_collection_image(self):
        return build_image_url(self.image)

    collection_image = property(get_collection_image)

    api_fields = ('name',
                  'description',
                  'collection_image')

    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
        FieldPanel('image'),
    ]

    def __str__(self):
        return self.name


register_snippet(BlogCollection)


class NoWebinarMessage(TranslatableMixin, models.Model):
    no_webinar_message = models.TextField()

    api_fields = ('no_webinar_message')

    panels = [
        FieldPanel('no_webinar_message')
    ]

    def __str__(self):
        return 'No Webinar Message'


register_snippet(NoWebinarMessage)


class WebinarCollection(TranslatableMixin, models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(default='')
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_collection_image(self):
        return build_image_url(self.image)

    collection_image = property(get_collection_image)

    api_fields = ('name',
                  'description',
                  'collection_image')

    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
        FieldPanel('image'),
    ]

    def __str__(self):
        return self.name


register_snippet(WebinarCollection)


class PromoteSnippet(TranslatableMixin, models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(default='')
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def get_promote_image(self):
        return build_image_url(self.image)
    promote_image = property(get_promote_image)

    api_fields = ('description',
                  'promote_image')

    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
        FieldPanel('image'),
    ]

    def __str__(self):
        return self.name


register_snippet(PromoteSnippet)


class AmazonBookBlurb(TranslatableMixin, models.Model):
    amazon_book_blurb = models.TextField()

    api_fields = ('amazon_book_blurb')

    panels = [
        FieldPanel('amazon_book_blurb')
    ]

    def __str__(self):
        return 'Amazon Book Blurb'


register_snippet(AmazonBookBlurb)


class ContentWarning(TranslatableMixin, models.Model):
    content_warning = models.TextField()

    api_fields = ('content_warning')

    panels = [
        FieldPanel('content_warning')
    ]

    def __str__(self):
        return (self.content_warning[:100] + '...') if len(self.content_warning) > 100 else self.content_warning



register_snippet(ContentWarning)
