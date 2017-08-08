from django.core.management.base import BaseCommand
from django.core.management import call_command

from concepts.models import Concept
from equations.management.commands import equations
from keywords.models import Keyword


class Command(BaseCommand):
    help = 'Remove redundant data'

    def handle(self, *args, **options):
        self.stdout.write('>> Cleaning concepts')
        info = Concept.objects.exclude(name='*').filter(conceptmeta__ref_count=0, conceptmeta__def_count=0).delete()
        self.stdout.write('Removed {} concepts'.format(info[1].get('concepts.Concept', 0)))

        self.stdout.write('>> Cleaning keywords')
        info = Keyword.objects.filter(itemkeyword__isnull=True, mediakeyword__isnull=True).delete()
        self.stdout.write('Removed {} keywords'.format(info[1].get('keywords.Keyword', 0)))

        self.stdout.write('>> Cleaning equations')
        call_command(equations.Command(), 'clean', stdout=self.stdout)

        self.stdout.write('Done')
