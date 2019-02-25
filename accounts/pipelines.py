from django.contrib.auth import logout

def save_profile(user, response, *args, **kwargs):
    if user:
        try:
            contact_infos = response.get('contact_infos')

            # grabbing the highest id in the email list to determine newest email
            newest_email = max(contact_infos, key=lambda x:x['id'])

            user.email = newest_email['value']
        except ValueError:
            user.email = 'none@openstax.org'
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

def social_user(backend, uid, user=None, *args, **kwargs):
    '''OVERRIDE: This will logout the current user
        instead of raising an exception '''

    provider = backend.name
    social = backend.strategy.storage.user.get_social_auth(provider, uid)
    if social:
        if user and social.user != user:
            logout(backend.strategy.request)
        elif not user:
            user = social.user
    return {'social': social,
            'user': user,
            'is_new': user is None,
            'new_association': False}