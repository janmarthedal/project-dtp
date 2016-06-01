import json
from django.conf import settings
#from django.core.urlresolvers import reverse
from django.db import models

from mathitems.itemtypes import ItemTypes

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


class Concept(models.Model):
    name = models.CharField(max_length=64, unique=True)


def convert_document(node, tag_map, eqn_map):
    new_node = {k: v for k, v in node.items() if k != 'children'}
    if node['type'] == 'tag-def':
        new_node['tag_id'] = tag_map[node['tag_id']]
    elif node['type'] == 'eqn':
        new_node['id'] = eqn_map[node['id']]
    if node.get('children'):
        new_node['children'] = [convert_document(child, tag_map, eqn_map)
                                for child in node['children']]
    return new_node


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
