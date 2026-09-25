from .models import Shipment, Event
from django.db import transaction
from django.http import JsonResponse
from django.db.utils import IntegrityError
from django.utils import timezone
from django.db.models import F
import time



def check_the_order(event_status, shipment_status):
    available_statuses = ['created', 'in_transit', 'delivered']
    index_of_event_status, index_of_shipment_status = available_statuses.index(event_status), available_statuses.index(shipment_status)
    if index_of_event_status <= index_of_shipment_status:
        return False
    return True


def processing_event(FAIL_ONCE_EVENT_ID=None):
    event_id = None

    try:
        with transaction.atomic():
            try:
                event = Event.objects\
                    .filter(state='pending')\
                    .select_for_update()\
                    .earliest('created_at')
            except Event.DoesNotExist:
                print('Event.DoesNotExist')
                time.sleep(5)
                return

            event_id = event.event_id

            shipment = Shipment.objects.select_for_update().get(pk=event.shipment_id)

            event_status = event.incoming_status
            shipment_status = shipment.status

            if not check_the_order(event_status, shipment_status):
                event.state = 'done'
                event.outcome = 'ignored'
                event.processed_at = timezone.now()
                event.save(update_fields=['state', 'outcome', 'processed_at'])
                print(f'event: {event_id} was ignored')
            else:
                shipment.status = event_status
                shipment.save(update_fields=['status'])

                if FAIL_ONCE_EVENT_ID == event.event_id and event.attempts == 0:
                    raise RuntimeError("TEST ERROR")

                event.state = 'done'
                event.outcome = 'applied'
                event.processed_at = timezone.now()
                event.save(update_fields=['state', 'outcome', 'processed_at'])
                print(f'event: {event_id} was applied, shipment {shipment.pk} was chanhed')


    except Exception as e:
        if event_id is not None:
            Event.objects.filter(event_id=event_id).update(
                attempts=F("attempts") + 1,
                last_error=str(e)[:500]
            )
            print(f'Exception on event: {event_id}')
            time.sleep(5)
