from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

from mathitems.itemtypes import ItemTypes
from mathitems.models import MathItem
from project.server_com import prepare_item

#import logging
#logger = logging.getLogger(__name__)


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
        return prepare_item(body)
