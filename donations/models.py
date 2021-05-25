from django.db import models

class ThankYouNote(models.Model):
    thank_you_note = models.TextField(null=True, blank=True)
    user_info = models.TextField(null=True, blank=True)
    created = models.DateField(auto_now_add=True)
