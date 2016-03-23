from django.http import JsonResponse
from django.core.mail import send_mail

from rest_framework.decorators import api_view


@api_view(['POST'])
def send_contact_message(request):
    if request.method == 'POST':
        to_address = request.POST.get("to_address", "").split(',')
        from_name = request.POST.get("from_name", "")
        from_address = request.POST.get("from_address", "")
        from_string = '{} <{}>'.format(from_name, from_address)
        subject = request.POST.get("subject", "")
        message_body = request.POST.get("message_body", "")

        try:
            mail = send_mail(subject, message_body, from_string, to_address)
            data = {
                'sent': mail,
            }
        except:
            data = {
                'sent': 0,
            }

        return JsonResponse(data)
