from django.contrib.auth.models import Group
from social.apps.django_app.default.models import UserSocialAuth
from .functions import get_or_create_user_profile


def save_profile(user, response, *args, **kwargs):
    if user:
        try:
            contact_infos = response.get('contact_infos')

            # grabbing the highest id in the email list to determine newest email
            newest_email = max(contact_infos, key=lambda x:x['id'])

            user.email = newest_email['value']
        except ValueError:
            user.email = '{}@openstax.org'.format(user.username)
        user.save()


def update_email(user, response, *args, **kwargs):
    try:
        contact_infos = response.get('contact_infos')

        # grabbing the highest id in the email list to determine newest email
        newest_email = max(contact_infos, key=lambda x:x['id'])

        user.email = newest_email['value']
    except ValueError:
        user.email = "none@openstax.org"
    user.save()


def update_role(user, response, *args, **kwargs):
    self_reported_role = response.get('self_reported_role')
    faculty_status = response.get('faculty_status')
    applications = response.get('applications')

    if self_reported_role == 'student':
        group, created = Group.objects.get_or_create(name=self_reported_role.title())
        group.user_set.add(user)

    if faculty_status == 'confirmed_faculty':
        group, created = Group.objects.get_or_create(name='Faculty')
        group.user_set.add(user)

    if applications and 'OpenStax Tutor' in [app['name'] for app in applications]:
        group, created = Group.objects.get_or_create(name='Tutor')
        group.user_set.add(user)


def update_accounts_profile(user, response, *args, **kwargs):
    uuid = response.get('uuid')
    profile = get_or_create_user_profile(user)

    profile.uuid = uuid
    profile.save()


def update_faculty_status(user, response, *args, **kwargs):
    faculty_status = response.get('faculty_status')
    profile = get_or_create_user_profile(user)

    profile.faculty_status = faculty_status
    profile.save()
