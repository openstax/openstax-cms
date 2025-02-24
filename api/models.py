from django.db import models
from books.models import Book


class CustomizationRequest(models.Model):
    email = models.CharField(max_length=255)
    num_students = models.IntegerField()
    reason = models.TextField()
    modules = models.TextField()
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)


class FeatureFlag(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text='Create flag names with underscores to be more machine friendly. Eg. awesome_feature')
    description = models.TextField(blank=True, default='')
    feature_active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class WebviewSettings(models.Model):
    name = models.CharField(max_length=255, unique=True)
    value = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Webview Settings'
