from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

from mathitems.itemtypes import ItemTypes
from mathitems.models import MathItem, get_item_info
from project.server_com import prepare_item, render_item

import logging
logger = logging.getLogger(__name__)


def get_item_refs_node(node, refs):
    if 'item' in node:
        refs.add(node['item'])
    for child in node.get('children', []):
        get_item_refs_node(child, refs)

def get_item_refs(node):
    refs = set()
    get_item_refs_node(node, refs)
    return refs


class DraftItem(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    item_type = models.CharField(max_length=1, choices=ItemTypes.CHOICES)
    body = models.TextField(blank=True)

    def __str__(self):
        return '{} (Draft{})'.format(self.get_item_type_display(),
                                     ' {}'.format(self.id) if self.id else '')

    def get_absolute_url(self):
        return reverse('show-draft', args=[self.id])

    def prepare(self):
        body = self.body.strip()
        html = ''
        defined = []
        errors = []

        if body:
            item_data = prepare_item(body)
            item_refs = get_item_refs(item_data['document'])
            item_data['refs'] = get_item_info(item_refs)
            logger.info(item_data['refs'])
            tag_map = {int(key): value for key, value in item_data['tags'].items()}
            data = render_item(item_data)
            html = data['html']
            defined = [tag_map[id] for id in data['defined']]
            errors = data['errors']
        else:
            errors = ['A {} may not be empty'.format(self.get_item_type_display())]

        if self.item_type == ItemTypes.DEF:
            if not defined:
                errors.append('A {} must define at least one concept'.format(self.get_item_type_display()))
        else:
            if defined:
                errors.append('A {} may not define concepts'.format(self.get_item_type_display()))
            defined = None

        return {'html': html, 'defined': defined, 'errors': errors}

    def get_publish_data(self):
        return prepare_item(self.body)
