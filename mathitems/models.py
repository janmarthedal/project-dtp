import json
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

from mathitems.itemtypes import ItemTypes
from project.server_com import render_item

#import logging
#logger = logging.getLogger(__name__)


class MathItem(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    item_type = models.CharField(max_length=1, choices=ItemTypes.CHOICES)
    body = models.TextField()

    def __str__(self):
        return '{} {}'.format(self.get_item_type_display(), self.id)

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


def convert_document(node, tag_map, eqn_map):
    overrides = {}
    if 'tag_id' in node:
        overrides['tag_id'] = tag_map[node['tag_id']]
    if 'eqn_id' in node:
        overrides['eqn_id'] = eqn_map[node['eqn_id']]
    if node.get('children'):
        overrides['children'] = [convert_document(child, tag_map, eqn_map)
                                 for child in node['children']]
    return dict(node, **overrides) if overrides else node


def publish(user, item_type, data):
    tag_conversions = {}
    for id, name in data.get('tags', {}).items():
        concept = Concept.objects.get_or_create(name=name)[0]
        tag_conversions[int(id)] = concept.id
    eqn_conversions = {}
    for id, eqn_obj in data.get('eqns', {}).items():
        eqn = Equation.objects.get_or_create(
            format=eqn_obj['format'], math=eqn_obj['math'],
            defaults={'html': eqn_obj['html']})[0]
        eqn_conversions[int(id)] = eqn.id
    document = convert_document(data['document'], tag_conversions, eqn_conversions)
    item = MathItem(created_by=user, item_type=item_type, body=json.dumps(document))
    item.save()
    return item


def get_eqns_tags(node, eqns, tags):
    if 'eqn_id' in node:
        eqns.add(node['eqn_id'])
    if 'tag_id' in node:
        tags.add(node['tag_id'])
    for child in node.get('children', []):
        get_eqns_tags(child, eqns, tags)


def item_to_html(item):
    doc = json.loads(item.body)
    eqns = set()
    tags = set()
    get_eqns_tags(doc, eqns, tags)
    eqn_map = {item.id: {'html': item.html}
               for item in Equation.objects.filter(id__in=eqns)}
    tag_map = {item.id: item.name
               for item in Concept.objects.filter(id__in=tags)}
    data = render_item({
        'document': doc,
        'eqns': eqn_map,
        'tags': tag_map,
    })
    return data
