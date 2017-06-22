from django.core.management.base import BaseCommand
from django.utils import timezone

from equations.models import CachedEquation, Equation, RenderedEquation
from project.server_com import render_eqns


class Command(BaseCommand):
    help = 'Equation management'

    PAGE_SIZE = 100

    def add_arguments(self, parser):
        parser.add_argument('command', choices=['clean', 'rerender'])

    def handle(self, *args, **options):
        if options['command'] == 'rerender':
            self.rerender()
        elif options['command'] == 'clean':
            self.clean()

    def rerender(self):
        count = Equation.objects.count()
        self.stdout.write('Rerendering {} equations'.format(count))

        start = 0
        while start < count:
            stop = min(start + self.PAGE_SIZE, count)
            self.stdout.write('Rendering {}-{}'.format(start, stop-1))

            to_render = {}
            object_map = {}
            for eqn in Equation.objects.all()[start:stop]:
                to_render[eqn.id] = {'format': eqn.format, 'math': eqn.math}
                object_map[eqn.id] = eqn

            rendered_eqns = render_eqns(to_render)
            for key, data in rendered_eqns.items():
                eqn = object_map[int(key)]
                RenderedEquation.objects.update_or_create(eqn=eqn, defaults={'html': data.get('html', ''),
                                                                             'error': data.get('error', '')})

            start = stop

        self.stdout.write(self.style.SUCCESS('Done'))

    def clean(self):
        cached_count = CachedEquation.objects.count()
        self.stdout.write('Cached equations: {}'.format(cached_count))
        too_old = timezone.now() - timezone.timedelta(days=7)
        delete_info = CachedEquation.objects.filter(access_at__lt=too_old).delete()
        self.stdout.write('Purged equations: {}'.format(delete_info[1].get('equations.CachedEquation', 0)))
        self.stdout.write(self.style.SUCCESS('Done'))
