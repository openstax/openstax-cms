from django.contrib.auth.models import Group
from social.apps.django_app.default.models import UserSocialAuth

def save_profile(user, *args, **kwargs):
    # for now - setting email address to prevent issues, should update it
    # eventually
    if user:
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


def social_user(backend, uid, user=None, *args, **kwargs):
    """Return UserSocialAuth account for backend/uid pair or None if it
    doesn't exists.

    CHANGE: Raise AuthAlreadyAssociated if UserSocialAuth entry belongs to another
    user.
    INSTEAD: Set new UserSocialAuth to user if associated before.
    """
    social_user = UserSocialAuth.get_social_auth(backend.name, uid)
    if social_user:
        if user and social_user.user != user:
            social_user.user = user
            social_user.save()
        elif not user:
            user = social_user.user
    return {'social_user': social_user, 'user': user}