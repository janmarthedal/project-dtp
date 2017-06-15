from django.core.management.base import BaseCommand
from concepts.models import Concept
from django.core.management import call_command
from equations.management.commands import equations


class Command(BaseCommand):
    help = 'Remove redundant data'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning concepts')
        for concept in Concept.objects.exclude(name='*').filter(conceptmeta__ref_count=0, conceptmeta__def_count=0).all():
            self.stdout.write('  {}'.format(concept.name))
            concept.delete()

        self.stdout.write('Cleaning equations')
        call_command(equations.Command(), 'clean')
