from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage, S3StaticStorage


class MediaStorage(S3Boto3Storage):
    def get_default_settings(self):
        default_settings = super().get_default_settings()
        default_settings.update(
            {
                "bucket_name": settings.MEDIA_BUCKET_NAME,
                "endpoint_url": settings.MEDIA_ENDPOINT_URL,
                "custom_domain": settings.MEDIA_CUSTOM_DOMAIN,
            }
        )
        return default_settings


class StaticStorage(S3StaticStorage):
    def get_default_settings(self):
        default_settings = super().get_default_settings()
        default_settings.update(
            {
                "bucket_name": settings.STATIC_BUCKET_NAME,
                "endpoint_url": settings.STATIC_ENDPOINT_URL,
                "custom_domain": settings.STATIC_CUSTOM_DOMAIN,
            }
        )
        return default_settings
