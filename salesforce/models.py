from django.db import models


class Adopter(models.Model):
    sales_id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True)
    website = models.URLField(max_length=255, null=True)

    def __str__(self):
        return self.name


class School(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
