from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.core.management.commands import dumpdata


class Command(BaseCommand):
    help = 'Backup all relevant data'

    def handle(self, *args, **options):
        call_command(dumpdata.Command(), exclude=[
            'auth.permission',
            'auth.group',
            'concepts.conceptdefinition',
            'concepts.conceptmeta',
            'concepts.conceptreference',
            'concepts.itemdependency',
            'contenttypes',
            'equations.ItemEquation',
            'equations.RenderedEquation',
            'sessions'
        ])
