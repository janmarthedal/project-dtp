from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

from mathitems.itemtypes import ItemTypes
from mathitems.models import MathItem, get_item_info
from project.server_com import prepare_item, render_item

#import logging
#logger = logging.getLogger(__name__)


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
        document = None
        html = ''
        defined = []
        refs = {}
        eqns = {}
        errors = []

        if body:
            prep_data = prepare_item(body)
            document = prep_data['document']
            refs = get_item_info(get_item_refs(document))
            eqns = prep_data['eqns']
            render_data = render_item(dict(prep_data, refs=refs))
            html = render_data['html']
            defined = render_data['defined']
            errors = render_data['errors']
        else:
            errors = ['A {} may not be empty'.format(self.get_item_type_display())]

        if self.item_type == ItemTypes.DEF:
            if not defined:
                errors.append('A {} must define at least one concept'.format(self.get_item_type_display()))
        else:
            if defined:
                errors.append('A {} may not define concepts'.format(self.get_item_type_display()))
            defined = None

        return {
            'document': document,
            'html': html,
            'defined': defined,
            'refs': refs,
            'eqns': eqns,
            'errors': errors,
        }
