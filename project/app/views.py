from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db import transaction
from django.db.utils import IntegrityError
from .models import Event, Shipment
import json
import hmac
import hashlib


def verify_signature(request):
    secret = "CarrierEvent"
    signature = request.headers.get('X-Webhook-Secret')

    if signature is None:
        return False

    return bool(secret == signature)


@csrf_exempt
def webhook_recipient_event(request):
    if request.method == 'POST':
        if verify_signature(request) is False:
            return JsonResponse({"detail": "Unauthorized"}, status=401)

        try:
            data = json.loads(request.body)
            print('data:', data)
        except json.JSONDecodeError:
            return JsonResponse({"detail": "JSONDecodeError"}, status=404)

        status = data.get('status')
        event_id = data.get('event_id')
        shipment_id = data.get('shipment_id')

        if not isinstance(event_id, str) or not (1 <= len(event_id) <= 64):
            return JsonResponse({"detail": "Wrong type or length of event_id"}, status=400)
        if status != 'in_transit' and status != 'delivered':
            return JsonResponse({"detail": "Wrong status"}, status=400)
        if type(shipment_id) is not int or shipment_id is None:
            return JsonResponse({"detail": "Wrong shipment_id"}, status=400)

        shipment_obj = Shipment.objects.filter(pk=shipment_id).first()
        if shipment_obj is None:
            return JsonResponse({"detail": "Shipment not found"}, status=404)

        event_object = Event.objects.filter(event_id=event_id).values_list('incoming_status', 'shipment_id').first()
        if event_object is not None:
            if event_object[0] != status or event_object[1] != shipment_id:
                return JsonResponse({"detail": "Change rejected"}, status=409)
            else:
                return JsonResponse({"event_id": event_id}, status=200)

        try:
            Event.objects.create(
                event_id=event_id,
                shipment_id=shipment_id,
                incoming_status=status,
            )
        except IntegrityError:
            event_obj = Event.objects.get(event_id=event_id)
            if event_obj.incoming_status == status and event_obj.shipment_id == shipment_id:
                return JsonResponse({"event_id": event_id}, status=200)
            return JsonResponse({"detail": "Change rejected"}, status=409)

        return JsonResponse({"event_id": event_id}, status=202)


def get_shipment(request, pk):
    if request.method == 'GET':
        shipment = get_object_or_404(Shipment, pk=pk)
        return JsonResponse({'shipment_id': shipment.pk, 'status': shipment.status})


def get_event(request, event_id):
    if request.method == 'GET':
        event = get_object_or_404(Event, event_id=event_id)
        return JsonResponse({
            'event_id': event.event_id,
            'shipment': event.shipment_id,
            'incoming_status': event.incoming_status,
            'state': event.state,
            'attempts': event.attempts,
            'last_error': event.last_error,
            'created_at': event.created_at,
            'processed_at': event.processed_at,
            'outcome': event.outcome,
        })
