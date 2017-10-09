from django.db import models


class Mail(models.Model):
    subject = models.CharField(max_length=255)
    to_address = models.EmailField()

    def __str__(self):
        return self.subject
