from django.db import models
from django.utils import timezone

from mathitems.models import MathItem
from project.server_com import render_eqns


# alter table equations convert to character set utf8 collate utf8_bin;

class Equation(models.Model):
    format = models.CharField(max_length=10)  # inline-TeX, TeX
    math = models.TextField()
    cache_access = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'equations'
        #unique_together = ('format', 'math')   # not possible for mysql

    def __str__(self):
        math = self.math
        if len(math) > 40:
            math = math[:37] + '...'
        return '{} ({})'.format(math, self.format)

    def check_cache_access(self):
        if self.cache_access:
            self.cache_access = timezone.now()
            self.save()

    def to_markup(self):
        if self.format == 'TeX':
            return '$${}$$'.format(self.math)
        return '${}$'.format(self.math)


class RenderedEquation(models.Model):
    eqn = models.OneToOneField(Equation, models.CASCADE, primary_key=True)
    html = models.TextField(blank=True)
    error = models.CharField(max_length=256, blank=True)

    class Meta:
        db_table = 'rendered_eqn'

    def get_html(self):
        if self.error:
            return {'error': self.error}
        return {'id': self.pk, 'html': self.html}   # id used by publish_equations


class ItemEquation(models.Model):
    item = models.ForeignKey(MathItem, db_index=True)
    equation = models.ForeignKey(Equation, db_index=True)

    class Meta:
        db_table = 'item_eqns'
        unique_together = ('item', 'equation')


def publish_equations(eqns):
    Equation.objects.filter(id__in=[data['id'] for data in eqns.values()]).update(cache_access=None)
    return {int(id): data['id'] for id, data in eqns.items()}


def get_equation_html(eqns):
    rendered_eqns = {}
    to_render = {}
    eqn_map = {}    # local key to Equation instance

    for key, data in eqns.items():
        if data.get('error'):
            rendered_eqns[key] = data
        else:
            eqn, created = Equation.objects.get_or_create(format=data['format'], math=data['math'])
            if not hasattr(eqn, 'renderedequation'):
                # this might happen if the data has been cleared (e.g., before a backup)
                eqn.check_cache_access()
                created = True
            if created:
                to_render[key] = data
                eqn_map[key] = eqn
            else:
                eqn.check_cache_access()
                rendered_eqns[key] = eqn.renderedequation.get_html()

    if to_render:
        new_rendered_eqns = render_eqns(to_render)
        for key, data in new_rendered_eqns.items():
            rendered_equation = RenderedEquation.objects.create(eqn=eqn_map[key], html=data.get('html', ''),
                                                                error=data.get('error', ''))
            rendered_eqns[key] = rendered_equation.get_html()

    return rendered_eqns
