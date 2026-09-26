import json
import os
import sys
import django
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.conf import settings


def forming_data():
    url = 'http://localhost:8000/webhooks/delivery'

    headers = {'content-type': 'application/json', 'X-Webhook-Secret': settings.SECRET_WEBHOOK}
    data_1 = [{"event_id": 'e1', "shipment_id": 1, "status": 'in_transit'}]

    data_2 = [{"event_id": 'e1', "shipment_id": 1, "status": 'delivered'},
              {"event_id": 'e1', "shipment_id": 1, "status": 'in_transit'}]

    data_3 = [{"event_id": 'e2', "shipment_id": 1, "status": 'delivered'}]

    for elem in data_3:
        res = requests.post(url, json=elem, headers=headers)
        print(res.text)



forming_data()