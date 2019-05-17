from django.db import models
from django.core.exceptions import ValidationError


class AuthSettings(models.Model):
    signed_encrypted_salt = models.CharField(max_length=255, null=True, blank=True)
    encrypted_salt = models.CharField(max_length=255, null=True, blank=True)
    cookie_name = models.CharField(max_length=255, null=True, blank=True)
    secret_base_key = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if SalesforceSettings.objects.exists() and not self.pk:
            raise ValidationError('There is can be only one SalesforceSettings instance')
        return super(SalesforceSettings, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Salesforce Settings"
