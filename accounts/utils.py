from .backend import OpenStax
from django.conf import settings
from social.strategies.django_strategy import DjangoStrategy 
from social.apps.django_app.default.models import DjangoStorage


IMPORT_PIPELINE = (
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.create_user',
    'accounts.pipelines.save_profile',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.user.user_details',
)

def create_user(**user_details):
    strategy = DjangoStrategy(DjangoStorage)
    openstax = OpenStax(strategy=strategy)
    result = openstax.run_pipeline(pipeline=IMPORT_PIPELINE,details=user_details,uid=user_details['uid'])
    return result
