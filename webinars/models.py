from django.db import models

class Webinar(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    speakers = models.CharField(max_length=255)
    spaces_remaining = models.PositiveIntegerField()
    registration_url = models.URLField()
    registration_link_text = models.CharField(max_length=255)
    display_on_tutor_page = models.BooleanField(default=False)

    def __str__(self):
        return self.title
