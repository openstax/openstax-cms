from django.db import models

class ProgressTracker(models.Model):
    account_id = models.IntegerField()
    progress = models.IntegerField()

    def __str__(self):
        return self.account_id


class CustomizationRequest(models.Model):
    email = models.CharField(max_length=255)
    num_students = models.IntegerField()
    reason = models.TextField()
    modules = models.TextField()
