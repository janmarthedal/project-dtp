from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

from project.helpers import node_request

class ItemTypes:
    DEF = 'D'
    THM = 'T'
    PRF = 'P'
    NAMES = {
        DEF: 'Definition',
        THM: 'Theorem',
        PRF: 'Proof',
    }
    CHOICES = tuple(NAMES.items())

class DraftItem(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
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
        item_data = node_request('/prepare-item', {'text': self.body})
        tag_map = {int(key): value for key, value in item_data['tags'].items()}
        data = node_request('/render-item', item_data)
        defined = [tag_map[id] for id in data['defined']]
        errors = data['errors']
        if self.item_type == ItemTypes.DEF:
            if not defined:
                errors.append('A {} must define at least one concept'.format(self.get_item_type_display()))
        else:
            if defined:
                errors.append('A {} may not define concepts'.format(self.get_item_type_display()))
            defined = None
        return {'html': data['html'], 'defined': defined, 'errors': errors}
