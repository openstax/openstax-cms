from django.conf import settings
from storages.backends.s3boto import S3BotoStorage
from django.contrib.staticfiles.storage import ManifestFilesMixin
from whitenoise.storage import CompressedManifestStaticFilesStorage


class StaticStorage(S3BotoStorage):
    location = settings.STATICFILES_LOCATION


class ManifestS3Storage(CompressedManifestStaticFilesStorage, StaticStorage):
    pass


class MediaStorage(S3BotoStorage):
    location = settings.MEDIAFILES_LOCATION
    file_overwrite = False
