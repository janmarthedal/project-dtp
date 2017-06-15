from django.core.management.base import BaseCommand
from media.models import SVGImage, CindyMedia


class Command(BaseCommand):
    help = 'List of media files'

    def handle(self, *args, **options):
        for item in SVGImage.objects.filter(parent__isnull=False):
            self.stdout.write(item.path)
        for item in CindyMedia.objects.filter(parent__isnull=False):
            self.stdout.write(item.path)
