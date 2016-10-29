from django.db import models
from django.db.utils import IntegrityError
from django.utils import timezone

from project.server_com import render_eqns


class Equation(models.Model):
    format = models.CharField(max_length=10)  # inline-TeX, TeX
    math = models.TextField()
    html = models.TextField()
    draft_access_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'equations'
        unique_together = ('format', 'math')

    def __str__(self):
        math = self.math
        if len(math) > 40:
            math = math[:37] + '...'
        return '{} ({})'.format(math, self.format)

    def to_source(self):
        if self.format == 'TeX':
            return '$${}$$'.format(self.math)
        return '${}$'.format(self.math)

    def to_data(self):
        return {'format': self.format, 'math': self.math, 'html': self.html}


def get_equation_html(eqns):
    rendered_eqns = {}
    to_render = {}

    for key, data in eqns.items():
        try:
            eqn = Equation.objects.get(format=data['format'], math=data['math'])
            if eqn.draft_access_at:  # cached draft equation?
                eqn.draft_access_at = timezone.now()
                eqn.save()
            rendered_eqns[key] = eqn.to_data()
        except Equation.DoesNotExist:
            to_render[key] = data

    new_rendered_eqns = render_eqns(to_render)
    for key, data in new_rendered_eqns.items():
        try:
            eqn = Equation.objects.create(format=data['format'], math=data['math'], html=data['html'])
        except IntegrityError:
            eqn = Equation.objects.get(format=data['format'], math=data['math'])
        rendered_eqns[key] = eqn.to_data()

    return rendered_eqns
