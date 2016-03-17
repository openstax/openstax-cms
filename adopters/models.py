from django.db import models
from modelcluster.fields import ParentalKey
from pages.models import AdoptersPage
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel
# Create your models here.

class Adopter(models.Model):
    salesforce_id = models.CharField(max_length=255, editable=False)
    name = models.CharField(max_length=255)
    description = RichTextField(null=True)
    website = models.URLField(max_length=255, null=True)

    page = ParentalKey(AdoptersPage,
                       on_delete=models.CASCADE,
                       related_name='adopters')

    api_fields = ('name', 'description', 'website')

    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
        FieldPanel('website'),
    ]

    def __str__(self):
        return self.name

