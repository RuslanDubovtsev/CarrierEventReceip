from django.db import models


class Event(models.Model):
    TYPE_STATUS = [
        ('in_transit', "in_transit"),
        ('delivered', 'delivered')
    ]

    TYPE_STATE = [
        ('pending', 'pending'),
        ('done', 'done')
    ]

    TYPE_OUTCOME = [
        ('ignored', 'ignored'),
        ('applied', 'applied')
    ]

    event_id = models.CharField(max_length=64, unique=True)
    shipment = models.ForeignKey("Shipment", on_delete=models.CASCADE)

    incoming_status = models.CharField(choices=TYPE_STATUS)
    state = models.CharField(choices=TYPE_STATE, default='pending')
    attempts = models.IntegerField(default=0)
    last_error = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    outcome = models.CharField(choices=TYPE_OUTCOME, null=True, blank=True)

    def __str__(self):
        return f'Event_id: {self.event_id} - {self.shipment}'


class Shipment(models.Model):
    TYPE_STATUS = [
        ('created', 'created'),
        ('in_transit', "in_transit"),
        ('delivered', 'delivered')
    ]

    status = models.CharField(choices=TYPE_STATUS, default='created')

    def __str__(self):
        return f'Shipment_id: {self.pk}'
