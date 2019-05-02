from django.conf import settings
from social.apps.django_app.default.models import DjangoStorage
from social.strategies.django_strategy import DjangoStrategy

from oxauth.backend import OpenStax


def create_user(**user_details):
    strategy = DjangoStrategy(DjangoStorage)
    openstax = OpenStax(strategy=strategy)
    result = openstax.run_pipeline(pipeline=settings.IMPORT_USER_PIPELINE,
                                   details=user_details,
                                   uid=user_details['uid'])
    user = result['user']
    return user
