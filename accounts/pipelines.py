def save_profile(backend, user, response, *args, **kwargs):
    #for now - setting email address to prevent issues, should update it eventually
    user.email = 'no-reply@openstax.org'
    user.save()
