import json
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

from mathitems.itemtypes import ItemTypes
from project.server_com import render_item

#import logging
#logger = logging.getLogger(__name__)


class MathItemManager(models.Manager):
    def get_by_name(self, name):
        return self.get(item_type=name[0], id=int(name[1:]))


class MathItem(models.Model):
    objects = MathItemManager()

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    item_type = models.CharField(max_length=1, choices=ItemTypes.CHOICES)
    body = models.TextField()

    def get_name(self):
        return self.item_type + str(self.id)

    def __str__(self):
        return '{} {}'.format(self.get_item_type_display(), self.get_name())

    def get_absolute_url(self):
        if self.item_type == ItemTypes.DEF:
            return reverse('show-def', args=[self.id])
        if self.item_type == ItemTypes.THM:
            return reverse('show-thm', args=[self.id])


class Equation(models.Model):
    class Meta:
        unique_together = ['format', 'math']
    format = models.CharField(max_length=10)  # inline-TeX, TeX
    math = models.TextField()
    html = models.TextField()

    def __str__(self):
        math = self.math
        if len(math) > 40:
            math = math[:37] + '...'
        return '{} ({})'.format(math, self.format)


class Concept(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


def encode_document(node, eqn_map):
    overrides = {}
    if 'concept' in node:
        concept = Concept.objects.get_or_create(name=node['concept'])[0]
        overrides['concept'] = concept.id
    if 'eqn_id' in node:
        overrides['eqn_id'] = eqn_map[node['eqn_id']]
    if node.get('children'):
        overrides['children'] = [encode_document(child, eqn_map)
                                 for child in node['children']]
    return dict(node, **overrides) if overrides else node


def publish(user, item_type, data):
    eqn_conversions = {}
    for id, eqn_obj in data.get('eqns', {}).items():
        eqn = Equation.objects.get_or_create(
            format=eqn_obj['format'], math=eqn_obj['math'],
            defaults={'html': eqn_obj['html']})[0]
        eqn_conversions[int(id)] = eqn.id
    document = encode_document(data['document'], eqn_conversions)
    item = MathItem(created_by=user, item_type=item_type, body=json.dumps(document))
    item.save()
    return item


def decode_document(node, eqns):
    overrides = {}
    if 'concept' in node:
        overrides['concept'] = Concept.objects.get(id=node['concept']).name
    if 'eqn_id' in node:
        eqns.add(node['eqn_id'])
    if node.get('children'):
        overrides['children'] = [decode_document(child, eqns)
                                 for child in node['children']]
    return dict(node, **overrides) if overrides else node


def item_to_html(item):
    eqns = set()
    doc = decode_document(json.loads(item.body), eqns)
    eqn_map = {item.id: {'html': item.html}
               for item in Equation.objects.filter(id__in=eqns)}
    return render_item({
        'document': doc,
        'eqns': eqn_map,
    })


def get_item_info(item_names):
    info = {}
    for item_name in item_names:
        try:
            item = MathItem.objects.get_by_name(item_name)
            info[item_name] = {
                'url': item.get_absolute_url(),
            }
        except MathItem.DoesNotExist:
            pass
    return info
