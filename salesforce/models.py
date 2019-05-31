from django.db import models
from django.core.exceptions import ValidationError

class Adopter(models.Model):
    sales_id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True)
    website = models.URLField(max_length=255, null=True)

    def __str__(self):
        return self.name


class School(models.Model):
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
    dataset_id = models.CharField(max_length=255)

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
