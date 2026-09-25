from django.core.management.base import CommandError, BaseCommand
from app.models import Event, Shipment
from app.worker_logic import processing_event


class Command(BaseCommand):
    help = "launches a worker"

    def add_arguments(self, parser):
        parser.add_argument(
            "--start",
            action="store_true",
            help='--start is a flag for launch worker'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('processing started')
        )
        while options['start']:
            processing_event('e2')


