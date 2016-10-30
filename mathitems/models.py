import json
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models

from mathitems.itemtypes import ItemTypes

import logging
logger = logging.getLogger(__name__)


class IllegalMathItem(Exception):
    pass


class MathItemManager(models.Manager):
    def get_by_name(self, name):
        return self.get(item_type=name[0], id=int(name[1:]))


class MathItem(models.Model):
    objects = MathItemManager()

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    item_type = models.CharField(max_length=1, choices=ItemTypes.CHOICES)
    parent = models.ForeignKey('self', null=True, blank=True)
    body = models.TextField()

    class Meta:
        db_table = 'mathitems'

    def get_name(self):
        return self.item_type + str(self.id)

    def __str__(self):
        return '{} {}'.format(self.get_item_type_display(), self.get_name())

    def clean(self):
        if self.item_type == ItemTypes.PRF:
            if not self.parent or self.parent.item_type != ItemTypes.THM:
                raise ValidationError('A Proof must have a Theorem parent')
        elif self.parent:
            raise ValidationError('A {} may not have a parent'.format(self.get_item_type_display()))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('show-item', args=[self.get_name()])

    def is_def(self):
        return self.item_type == ItemTypes.DEF

    def analyze(self):
        eqns = set()
        concept_defs = set()
        concept_refs = set()
        item_refs = {}
        root = json.loads(self.body)
        analyze_node(root, eqns, concept_defs, concept_refs, item_refs)
        return eqns, concept_defs, concept_refs, item_refs

    #def to_source(self):
    #    return node_to_source_text(json.loads(self.body))

def analyze_node(node, eqns, concept_defs, concept_refs, item_refs):
    if node['type'] == 'eqn':
        eqns.add(node['eqn'])
    elif node['type'] == 'concept-def':
        concept_defs.add(node['concept'])
    elif node['type'] == 'concept-ref':
        concept_refs.add(node['concept'])
    elif node['type'] == 'item-ref':
        item_id = node['item']
        if item_id in item_refs:
            data = item_refs[item_id]
        else:
            item_refs[item_id] = data = {'whole': False}
        if 'concept' in node:
            if 'concepts' not in data:
                data['concepts'] = set()
            data['concepts'].add(node['concept'])
        else:
            data['whole'] = True
    for child in node.get('children', []):
        analyze_node(child, eqns, concept_defs, concept_refs, item_refs)

"""def node_to_source_text(node):
    if node['type'] == 'text':
        return node['value']
    if node['type'] == 'eqn':
        return Equation.objects.get(id=node['eqn']).to_source()
    children = [node_to_source_text(child) for child in node.get('children', [])]
    if node['type'] == 'body':
        return '\n\n'.join(children)
    if node['type'] == 'para':
        return ''.join(children)
    concept = Concept.objects.get(id=node['concept']).name if 'concept' in node else None
    if node['type'] == 'concept-ref':
        return '[{}]({})'.format(''.join(children), concept)
    if node['type'] == 'concept-def':
        return '[{}](={})'.format(''.join(children), concept)
    if node['type'] == 'item-ref':
        ref = node['item']
        if concept:
            ref = '{}#{}'.format(ref, concept)
        return '[{}]({})'.format(''.join(children), ref)
"""
