import json
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models

from mathitems.itemtypes import ItemTypes
from project.server_com import render_item

import logging
logger = logging.getLogger(__name__)


class IllegalMathItem(Exception):
    pass


class Concept(models.Model):
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        db_table = 'concepts'

    def __str__(self):
        return self.name


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

    def render(self):
        eqns = set()
        document = decode_document(json.loads(self.body), eqns)
        eqn_map = {equation.id: {'html': equation.html}
                   for equation in Equation.objects.filter(id__in=eqns)}
        result = get_refs_and_render(self.item_type, document, eqn_map)
        if result['errors']:
            raise IllegalMathItem('Error in published item {}'.format(self.id))
        del result['errors']
        return result

    def is_def(self):
        return self.item_type == ItemTypes.DEF

    def to_source(self):
        return node_to_source_text(json.loads(self.body))


class ConceptDefinition(models.Model):
    item = models.ForeignKey(MathItem, db_index=True)
    concept = models.ForeignKey(Concept, db_index=True)

    class Meta:
        db_table = 'concept_defs'


def encode_document(node, eqn_map, defines):
    overrides = {}
    if 'concept' in node:
        concept = Concept.objects.get_or_create(name=node['concept'])[0]
        overrides['concept'] = concept.id
        if node.get('type') == 'concept-def':
            defines[concept.id] = concept
    if 'eqn' in node:
        overrides['eqn'] = eqn_map[node['eqn']]
    if node.get('children'):
        overrides['children'] = [encode_document(child, eqn_map, defines)
                                 for child in node['children']]
    return dict(node, **overrides) if overrides else node


def publish(user, item_type, parent, document, eqns):
    eqn_conversions = {}
    for id, eqn_obj in eqns.items():
        eqn = Equation.objects.get_or_create(
            format=eqn_obj['format'], math=eqn_obj['math'],
            defaults={'html': eqn_obj['html']})[0]
        eqn_conversions[int(id)] = eqn.id
    defines = {}
    document = encode_document(document, eqn_conversions, defines)
    item = MathItem(created_by=user, item_type=item_type, body=json.dumps(document))
    if parent:
        item.parent = parent
    item.save()
    if item_type == ItemTypes.DEF:
        ConceptDefinition.objects.bulk_create(
            ConceptDefinition(item=item, concept=concept) for concept in defines.values())
    return item


def decode_document(node, eqns):
    overrides = {}
    if 'concept' in node:
        overrides['concept'] = Concept.objects.get(id=node['concept']).name
    if 'eqn' in node:
        eqns.add(node['eqn'])
    if node.get('children'):
        overrides['children'] = [decode_document(child, eqns)
                                 for child in node['children']]
    return dict(node, **overrides) if overrides else node


def get_node_refs(node, refs):
    if 'item' in node:
        refs.add(node['item'])
    for child in node.get('children', []):
        get_node_refs(child, refs)

def get_document_refs(document):
    item_names = set()
    get_node_refs(document, item_names)
    info = {}
    for item_name in item_names:
        try:
            item = MathItem.objects.get_by_name(item_name)
            data = {'url': item.get_absolute_url()}
            if item.item_type == ItemTypes.DEF:
                data['defines'] = list(Concept.objects.filter(conceptdefinition__item=item)
                                            .values_list('name', flat=True))
            info[item_name] = data
        except MathItem.DoesNotExist:
            pass
    return info


def get_refs_and_render(item_type, document, eqns):
    refs = get_document_refs(document)
    return render_item(item_type, document, eqns, refs)


def node_to_source_text(node):
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
