from django.urls import path
from .views import webhook_recipient_event, get_event, get_shipment

# url: delivery
urlpatterns = [
    path('webhooks/delivery', webhook_recipient_event, name='webhook_delivery'),
    path('shipment/<int:pk>', get_shipment, name='get_shipment'),
    path('event/<str:event_id>', get_event, name='get_event')
]
