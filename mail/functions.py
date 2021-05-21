from django.core.mail import EmailMessage, send_mail
import logging


def send_redirect_report(bad_redirects):
    msg = 'The Openstax Redirect Report has been run'
    msg += '\n\nShort Code,Redirect URL'
    msg += '\n' + str(bad_redirects)

    subject = 'OpenStax Redirect Report'
    from_address = 'noreply@openstax.org'
    to_address = ['cmsupport@openstax.org', ]

    try:
        email = EmailMessage(subject,
                             msg,
                             from_address,
                             to_address)
        email.send()

    except Exception as e:
        logger.error("EMAIL FAILED TO SEND: subject:{}".format(subject))
