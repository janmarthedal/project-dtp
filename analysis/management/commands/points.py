from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Recomputes all item/validation points'

    def handle(self, *args, **options):
        pass
