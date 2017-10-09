import logging

from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.middleware import csrf
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from rest_framework.decorators import api_view

from .models import Mail

@csrf_exempt
@api_view(['POST', 'GET'])
def send_contact_message(request):
    if request.method == 'POST':
        name = request.POST.get("from_name", "")
        from_name = name.replace(',', '')
        from_address = request.POST.get("from_address", "")
        from_string = '{} <{}>'.format(from_name, from_address)
        subject = request.POST.get("subject", "")
        message_body = request.POST.get("message_body", "")

        # Add subject: to_address to this dict to add a new email address.
        # Subject will map to the email being sent to to prevent misuse of our email server.
        mails = Mail.objects.all()
        emails = {mail.subject: mail.to_address for mail in mails}

        try:
            to_address = emails[subject].split(',')
            email = EmailMessage(subject,
                                 message_body,
                                 'noreply@openstax.org',
                                 to_address,
                                 reply_to=[from_string])
            email.send()
        except KeyError:
            logging.error("EMAIL FAILED TO SEND: subject:{}")

        if subject == "Bulk Order": # if this is a bulk order, send them to a special confirmation page
            return redirect('/confirmation/bulk-order')
        else: #otherwise, send them to the contact confirmation page
            return redirect('/confirmation/contact')

    # if this is not posting a message, let's send the csfr token back
    else:
        csrf_token = csrf.get_token(request)
        data = {'csrf_token': csrf_token}

        return JsonResponse(data)
