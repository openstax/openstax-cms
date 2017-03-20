from django.contrib.gis.geoip2 import GeoIP2
from django.http import JsonResponse
import requests

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def user_location(request):
    ip = get_client_ip(request)
    if ip == "127.0.0.1":
        ip = "128.42.54.215" #if local, use rice ip address
    g = GeoIP2()
    city = g.city(ip)
    return JsonResponse(city)


def calculate_taxes(request, amount):
    print(amount)
    headers = {"Authorization": "Bearer 540d7d339cf2b32fca273bf44cde2515", "Content-Type": "application/json"}
    payload = {
        "from_country": "US",
        "from_zip": "77005",
        "from_state": "TX",
        "from_city": "Houston",
        "from_street": "6100 Main St",
        "to_country": "US",
        "to_zip": "78249",
        "to_state": "TX",
        "to_city": "San Antonio",
        "to_street": "1 UTSA Circle",
        "amount": amount,
        "shipping": 0,
        "nexus_addresses": [
          {
            "id": "Main Campus",
            "country": "US",
            "zip": "77005",
            "state": "TX",
            "city": "Houston",
            "street": "6100 Main Street"
          }
        ],
        "line_items": [
          {
            "id": "1",
            "quantity": 1,
            "product_tax_code": "30070",
            "unit_price": amount,
            "discount": 0
          }
        ]
    }
    r = requests.post('https://api.taxjar.com/v2/taxes', headers=headers, json=payload)
    return JsonResponse(r.json())


def tax_rate(request, zip):
    headers = {"Authorization": "Bearer 540d7d339cf2b32fca273bf44cde2515"}
    r = requests.get('https://api.taxjar.com/v2/rates/{}'.format(zip), headers=headers)
    return JsonResponse(r.json())