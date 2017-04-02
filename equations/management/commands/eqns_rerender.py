from django.core.management.base import BaseCommand

from equations.models import Equation
from project.server_com import render_eqns


class Command(BaseCommand):
    help = 'Rerender all equations'

    PAGE_SIZE = 100

    def handle(self, *args, **options):
        count = Equation.objects.count()
        self.stdout.write('Number of equations: {}'.format(count))

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
                if data.get('error'):
                    eqn.error = data['error']
                    eqn.html = ''
                else:
                    eqn.html = data['html']
                    eqn.error = ''
                eqn.save()

            start = stop

        self.stdout.write(self.style.SUCCESS('Done'))
