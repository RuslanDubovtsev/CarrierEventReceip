from django.contrib import admin
from .models import Shipment, Event

admin.site.register(Event)
admin.site.register(Shipment)