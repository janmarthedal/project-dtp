from django.db import models
from django.db.utils import IntegrityError
from django.utils import timezone

from mathitems.models import MathItem
from project.server_com import render_eqns


class Equation(models.Model):
    format = models.CharField(max_length=10)  # inline-TeX, TeX
    math = models.TextField()
    html = models.TextField()
    draft_access_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'equations'
        #unique_together = ('format', 'math')   # not possible for mysql

    def __str__(self):
        math = self.math
        if len(math) > 40:
            math = math[:37] + '...'
        return '{} ({})'.format(math, self.format)

    def to_markup(self):
        if self.format == 'TeX':
            return '$${}$$'.format(self.math)
        return '${}$'.format(self.math)

    def to_data(self):
        return {'format': self.format, 'math': self.math, 'html': self.html}


class ItemEquation(models.Model):
    item = models.ForeignKey(MathItem, db_index=True)
    equation = models.ForeignKey(Equation, db_index=True)

    class Meta:
        db_table = 'item_eqns'
        unique_together = ('item', 'equation')


def freeze_equations(eqns):
    conversion_map = {}
    for id, data in eqns.items():
        try:
            eqn = Equation.objects.get(format=data['format'], math=data['math'])
            if eqn.draft_access_at:
                eqn.draft_access_at = None
                eqn.save()
        except Equation.DoesNotExist:
            eqn = Equation.objects.create(format=data['format'], math=data['math'],
                                          html=data['html'], draft_access_at=None)
        conversion_map[int(id)] = eqn.id
    return conversion_map


def get_equation_html(eqns):
    rendered_eqns = {}
    to_render = {}

    for key, data in eqns.items():
        if data.get('error'):
            rendered_eqns[key] = data
        else:
            try:
                eqn = Equation.objects.get(format=data['format'], math=data['math'])
                if eqn.draft_access_at:
                    eqn.draft_access_at = timezone.now()
                    eqn.save()
                rendered_eqns[key] = eqn.to_data()
            except Equation.DoesNotExist:
                to_render[key] = data

    if to_render:
        new_rendered_eqns = render_eqns(to_render)
        for key, data in new_rendered_eqns.items():
            if data.get('error'):
                rendered_eqns[key] = data
            else:
                try:
                    eqn = Equation.objects.create(format=data['format'], math=data['math'], html=data['html'])
                except IntegrityError:
                    eqn = Equation.objects.get(format=data['format'], math=data['math'])
                rendered_eqns[key] = eqn.to_data()

    return rendered_eqns
