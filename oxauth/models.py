from django.contrib.auth.models import User
from django.db import models

# TODO: This can be removed, it's not being used but will do in another PR because it causing deployment issues.
class OpenStaxUserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    openstax_accounts_id = models.IntegerField()
    openstax_accounts_uuid = models.UUIDField()

    def __str__(self):
        return self.user.username
