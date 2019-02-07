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

