from django.conf import settings
from storages.backends.s3boto import S3BotoStorage


class MediaStorage(S3BotoStorage):
    location = settings.MEDIAFILES_LOCATION
    file_overwrite = False
