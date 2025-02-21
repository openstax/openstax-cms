import logging
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

logger = logging.getLogger(__name__)


class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION
    file_overwrite = False

    def _save(self, name, content):
        logger.info(f"Saving file {name} to S3")
        try:
            result = super()._save(name, content)
            logger.info(f"File {name} saved successfully to S3")
            return result
        except Exception as e:
            logger.error(f"Error saving file {name} to S3: {e}")
            raise