from django.db import models
from django.contrib.auth.models import User


class UserPendingVerification(models.Model):
    user = models.OneToOneField(User)
    pending_verification = models.BooleanField()
