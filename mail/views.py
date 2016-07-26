import logging

from django.core.mail import EmailMessage
from django.http import JsonResponse, Http404
from django.middleware import csrf
from django.shortcuts import redirect
from rest_framework.decorators import api_view


@api_view(['POST', 'GET'])
def send_contact_message(request):
    if request.method == 'POST':
        from_name = request.POST.get("from_name", "")
        from_address = request.POST.get("from_address", "")
        from_string = '{} <{}>'.format(from_name, from_address)
        subject = request.POST.get("subject", "")
        message_body = request.POST.get("message_body", "")

        emails = {
            'General OpenStax Question': 'info@openstax.org',
            'Adopting OpenStax Textbooks':  'info@openstax.org',
            'Concept Coach Question': 'ccsupport@openstax.org',
            'I\'m interested in piloting OpenStax Tutor': 'tutorpilot@openstax.org',
            'OpenStax Tutor Question': 'tutorsupport@openstax.org',
            'CNX Question': 'cnx@cnx.org',
            'Donations': 'info@openstax.org',
            'College/University Partnerships': 'info@openstax.org',
            'Media Inquiries': 'info@openstax.org',
            'Foundation': 'richb@rice.edu, dcwill@rice.edu, mka2@rice.edu',
            'OpenStax Partners': 'info@openstax.org',
            'Website': 'info@openstax.org',
        }

        try:
            to_address = emails[subject].split(',')
            email = EmailMessage(subject,
                                 message_body,
                                 from_address,
                                 to_address,
                                 reply_to=[from_string])
            email.send()
        except KeyError:
            logging.error("EMAIL FAILED TO SEND: subject:{}")

        return redirect('/contact-thank-you')
    # if this is not posting a message, let's send the csfr token back
    else:
        csrf_token = csrf.get_token(request)
        data = {'csrf_token': csrf_token}

        return JsonResponse(data)
