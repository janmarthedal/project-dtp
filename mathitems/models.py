import json
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

from mathitems.itemtypes import ItemTypes
from project.server_com import render_item

#import logging
#logger = logging.getLogger(__name__)


class Concept(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


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


class MathItemManager(models.Manager):
    def get_by_name(self, name):
        return self.get(item_type=name[0], id=int(name[1:]))


class MathItem(models.Model):
    objects = MathItemManager()

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    item_type = models.CharField(max_length=1, choices=ItemTypes.CHOICES)
    parent = models.ForeignKey('self', null=True)
    body = models.TextField()
    defines = models.ManyToManyField(Concept)

    def get_name(self):
        return self.item_type + str(self.id)

    def __str__(self):
        return '{} {}'.format(self.get_item_type_display(), self.get_name())

    def get_absolute_url(self):
        if self.item_type == ItemTypes.DEF:
            return reverse('show-def', args=[self.id])
        if self.item_type == ItemTypes.THM:
            return reverse('show-thm', args=[self.id])

    def render(self):
        eqns = set()
        document = decode_document(json.loads(self.body), eqns)
        eqn_map = {equation.id: {'html': equation.html}
                   for equation in Equation.objects.filter(id__in=eqns)}
        return get_refs_and_render(self.item_type, document, eqn_map)


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


def publish(user, item_type, document, eqns):
    eqn_conversions = {}
    for id, eqn_obj in eqns.items():
        eqn = Equation.objects.get_or_create(
            format=eqn_obj['format'], math=eqn_obj['math'],
            defaults={'html': eqn_obj['html']})[0]
        eqn_conversions[int(id)] = eqn.id
    defines = {}
    document = encode_document(document, eqn_conversions, defines)
    item = MathItem(created_by=user, item_type=item_type, body=json.dumps(document))
    item.save()
    if item_type == ItemTypes.DEF:
        item.defines = list(defines.values())
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
                data['defines'] = [concept.name for concept in item.defines.all()]
            info[item_name] = data
        except MathItem.DoesNotExist:
            pass
    return info


def get_refs_and_render(item_type, document, eqns):
    refs = get_document_refs(document)
    return render_item(item_type, document, eqns, refs)
