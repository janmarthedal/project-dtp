from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

from mathitems.itemtypes import ItemTypes
from project.helpers import node_request

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
            item_data = node_request('/prepare-item', {'text': body})
            tag_map = {int(key): value for key, value in item_data['tags'].items()}
            data = node_request('/render-item', item_data)
            html = data['html']
            defined = [tag_map[id] for id in data['defined']]
            errors = data['errors']
        elif self.item_type != ItemTypes.PRF:
            errors = ['A {} may not be empty'.format(self.get_item_type_display())]

        if self.item_type == ItemTypes.DEF:
            if not defined:
                errors.append('A {} must define at least one concept'.format(self.get_item_type_display()))
        else:
            if defined:
                errors.append('A {} may not define concepts'.format(self.get_item_type_display()))
            defined = None

        return {'html': html, 'defined': defined, 'errors': errors}
