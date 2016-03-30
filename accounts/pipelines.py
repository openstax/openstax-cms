def save_profile(user, *args, **kwargs):
    # for now - setting email address to prevent issues, should update it
    # eventually
    if user:
        user.email = '{}@openstax.org'.format(user.username)
        user.save()
