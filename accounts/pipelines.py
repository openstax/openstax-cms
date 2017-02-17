def save_profile(user, *args, **kwargs):
    # for now - setting email address to prevent issues, should update it
    # eventually
    if user:
        user.email = '{}@openstax.org'.format(user.username)
        user.save()


def update_email(user, response, *args, **kwargs):
    contact_infos = response.get('contact_infos')

    # grabbing the highest id in the email list to determine newest email
    newest_email = max(contact_infos, key=lambda x:x['id'])

    user.email = newest_email['value']
    user.save()
