import hashlib
from django.db import models
from django.utils import timezone

from mathitems.models import MathItem
from project.server_com import render_eqns


def calc_hash(format, math):
    return hashlib.md5((format + math).encode()).hexdigest()


class Equation(models.Model):
    format = models.CharField(max_length=10)  # inline-TeX, TeX
    math = models.TextField()

    class Meta:
        db_table = 'equations'

    def __str__(self):
        math = self.math
        if len(math) > 40:
            math = math[:37] + '...'
        return '{} ({})'.format(math, self.format)

    def to_markup(self):
        if self.format == 'TeX':
            return '$$\n{}\n$$'.format(self.math)
        return '${}$'.format(self.math)


class RenderedEquation(models.Model):
    eqn = models.OneToOneField(Equation, models.CASCADE, primary_key=True)
    hash = models.CharField(max_length=32, db_index=True)
    html = models.TextField(blank=True)
    error = models.CharField(max_length=256, blank=True)

    class Meta:
        db_table = 'rendered_eqn'

    def get_html(self):
        if self.error:
            return {'error': self.error}
        return {
            'source': 'rendered-eqn',
            'id': self.pk,
            'html': self.html
        }   # source+id used by publish_equations


class CachedEquation(models.Model):
    hash = models.CharField(max_length=32, db_index=True)
    format = models.CharField(max_length=10)  # inline-TeX, TeX
    math = models.TextField()
    access_at = models.DateTimeField(auto_now_add=True)
    html = models.TextField(blank=True)
    error = models.CharField(max_length=256, blank=True)

    class Meta:
        db_table = 'cached_eqn'

    def get_html(self):
        if self.error:
            return {'error': self.error}
        return {
            'source': 'cached-eqn',
            'id': self.pk,
            'html': self.html
        }   # source+id used by publish_equations


class ItemEquation(models.Model):
    item = models.ForeignKey(MathItem, db_index=True)
    equation = models.ForeignKey(Equation, db_index=True)

    class Meta:
        db_table = 'item_eqns'
        unique_together = ('item', 'equation')


def publish_equations(eqns):
    eqn_conv = {}
    for key, data in eqns.items():
        if data['source'] == 'cached-eqn':
            cached_eqn = CachedEquation.objects.get(pk=data['id'])
            eqn = Equation.objects.create(format=cached_eqn.format, math=cached_eqn.math)
            RenderedEquation.objects.create(eqn=eqn, html=cached_eqn.html,
                                            hash=calc_hash(cached_eqn.format, math=cached_eqn.math))
            cached_eqn.delete()
            eqn_conv[int(key)] = eqn.pk
        else:
            eqn_conv[int(key)] = data['id']
    return eqn_conv


def get_equation_html(eqns):
    rendered_eqns = {}
    to_render = {}

    for key, data in eqns.items():
        if data.get('error'):
            rendered_eqns[key] = data
        else:
            format = data['format']
            math = data['math']
            hash = calc_hash(format, math)
            try:
                reqn = RenderedEquation.objects.get(hash=hash, eqn__format=format, eqn__math=math)
                rendered_eqns[key] = reqn.get_html()
            except RenderedEquation.DoesNotExist:
                try:
                    cached_eqn = CachedEquation.objects.get(hash=hash, format=format, math=math)
                    cached_eqn.access_at = timezone.now()
                    cached_eqn.save()
                    rendered_eqns[key] = cached_eqn.get_html()
                except CachedEquation.DoesNotExist:
                    to_render[key] = data

    if to_render:
        new_rendered_eqns = render_eqns(to_render)
        for key, out_data in new_rendered_eqns.items():
            in_data = eqns[key]
            format = in_data['format']
            math = in_data['math']
            hash = calc_hash(format, math)
            cached_eqn, created = CachedEquation.objects.get_or_create(
                hash=hash, format=format, math=math,
                defaults={'html': out_data.get('html', ''),
                          'error': out_data.get('error', '')})
            rendered_eqns[key] = cached_eqn.get_html()

    return rendered_eqns
