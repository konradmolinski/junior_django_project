from django.core.management.base import BaseCommand, CommandError
from images.models import BinaryImage
import pytz
from django.conf import settings
import datetime

timezone = pytz.timezone(settings.TIME_ZONE)


class Command(BaseCommand):
    help = "Deletes all BinaryImage objects with expiration time lessen then now."

    def handle(self, *args, **options):
        queryset = BinaryImage.objects.filter(expiration_date__lt=timezone.localize(datetime.datetime.now()))
        queryset.delete()