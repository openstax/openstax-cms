from django.contrib.auth.models import User
from django.db import models

class OpenStaxUserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    openstax_accounts_id = models.IntegerField()
    openstax_accounts_uuid = models.UUIDField()
