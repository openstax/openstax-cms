def save_profile(backend, user, response, *args, **kwargs):
    #for now - setting email address to prevent issues, should update it eventually
    user.email = '{}@openstax.org'.format(user.username)
    user.save()
