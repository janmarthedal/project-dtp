import json
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

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

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    item_type = models.CharField(max_length=1, choices=ItemTypes.CHOICES)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
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

    def is_thm(self):
        return self.item_type == ItemTypes.THM

    def get_body_root(self):
        return json.loads(self.body)

    def analyze(self):
        eqns = set()
        concept_defs = set()
        concept_refs = set()
        item_refs = {}
        media_refs = set()
        root = self.get_body_root()
        analyze_node(root, eqns, concept_defs, concept_refs, item_refs, media_refs)
        return eqns, concept_defs, concept_refs, item_refs, media_refs


def analyze_node(node, eqns, concept_defs, concept_refs, item_refs, media_refs):
    if node['type'] == 'eqn':
        eqns.add(node['eqn'])
    elif node['type'] == 'concept-def':
        concept_defs.add(node['concept'])
    elif node['type'] == 'concept-ref':
        concept_refs.add(node['concept'])
    elif node['type'] == 'media':
        media_refs.add(node['media'])
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
        analyze_node(child, eqns, concept_defs, concept_refs, item_refs, media_refs)


# keep in sync with function in javascript/src/markup-to-ast.js
def concept_to_label(con):
    r = con.split('/')[-1]
    return r.replace('-', ' ') if r else con


def node_to_markup(node, concept_map, eqn_map):
    if node['type'] == 'break':
        return '{}\n'.format('  ' if node.get('hard') else '')
    if node['type'] == 'code':
        return '`{}`'.format(node['value'])
    if node['type'] == 'codeblock':
        return '```{}\n{}```\n'.format(node.get('info', ''), node['value'])
    if node['type'] == 'eqn':
        return eqn_map[node['eqn']]
    if node['type'] == 'list':
        items = []
        for child in node.get('children', []):
            if child['type'] != 'list-item':
                raise Exception('Expected list-item')
            children = [node_to_markup(child2, concept_map, eqn_map) for child2 in child.get('children', [])]
            items.append('\n\n'.join(children).split('\n'))
        item_strings = []
        if node.get('ordered'):
            counter = node.get('listStart', 1)
            delim = node.get('listDelimiter')
            for lines in items:
                prefix = '{}{} '.format(counter, delim)
                joiner = '\n' + (' ' * len(prefix))
                item_strings.append(prefix + joiner.join(lines))
                counter += 1
        else:
            item_strings = ('* {}'.format('\n  '.join(p)) for p in items)
        return '\n'.join(item_strings)
    if node['type'] == 'ruler':
        return '---\n'
    if node['type'] == 'text':
        return node['value']

    children = [node_to_markup(child, concept_map, eqn_map) for child in node.get('children', [])]
    if node['type'] == 'blockquote':
        return '> ' + '\n> '.join('\n\n'.join(children).split('\n'))
    if node['type'] == 'document':
        return '\n\n'.join(children)

    child_markup = ''.join(children)

    if node['type'] == 'emph':
        return '*{}*'.format(child_markup)
    if node['type'] == 'heading':
        return '{} {}'.format('#' * node['level'], child_markup)
    if node['type'] == 'para':
        return child_markup
    if node['type'] == 'strong':
        return '**{}**'.format(child_markup)

    con = concept_map[node['concept']] if 'concept' in node else None
    if concept_to_label(con) == child_markup:
        child_markup = ''

    if node['type'] == 'concept-ref':
        return '[{}](#{})'.format(child_markup, con)
    if node['type'] == 'concept-def':
        return '[{}](={})'.format(child_markup, con)
    if node['type'] == 'item-ref':
        ref = node['item']
        if con:
            ref += '#{}'.format(con)
        return '[{}]({})'.format(child_markup, ref)
    raise Exception('Unsupported AST node {}'.format(node['type']))
