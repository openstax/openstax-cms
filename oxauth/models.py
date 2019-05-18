from django.db import models
from django.core.exceptions import ValidationError


class AuthSettings(models.Model):
    signed_encrypted_salt = models.CharField(max_length=255, null=True, blank=True)
    encrypted_salt = models.CharField(max_length=255, null=True, blank=True)
    cookie_name = models.CharField(max_length=255, null=True, blank=True)
    secret_base_key = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.pk)

    def save(self, *args, **kwargs):
        if AuthSettings.objects.exists() and not self.pk:
            raise ValidationError('There is can be only one AuthSettings instance')
        return super(AuthSettings, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Auth Settings"
