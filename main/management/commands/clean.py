import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command

from concepts.models import Concept
from equations.management.commands import equations
from keywords.models import Keyword
from media.models import all_file_paths


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

        self.stdout.write('>> Cleaning media files')
        media_paths = set(all_file_paths())
        for (dirpath, dirnames, filenames) in os.walk(settings.MEDIA_ROOT):
            for filename in filenames:
                path = os.path.join(dirpath, filename)
                self.stdout.ending = ''
                self.stdout.write(path)
                self.stdout.ending = '\n'
                if filename[0] == '.' or path in media_paths:
                    self.stdout.write(' - keep')
                else:
                    self.stdout.write(' - remove')
                    os.remove(path)

        self.stdout.write('Done')
