from .backend import OpenStax
from django.conf import settings
from social.strategies.django_strategy import DjangoStrategy
from social.apps.django_app.default.models import DjangoStorage


def create_user(**user_details):
    strategy = DjangoStrategy(DjangoStorage)
    openstax = OpenStax(strategy=strategy)
    result = openstax.run_pipeline(pipeline=settings.IMPORT_USER_PIPELINE,
                                   details=user_details, 
                                   uid=user_details['uid'])
    return result
