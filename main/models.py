from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

from project.helpers import capfirst

class ItemTypes:
    DEF = 'D'
    THM = 'T'
    PRF = 'P'
    NAMES = {
        DEF: 'definition',
        THM: 'theorem',
        PRF: 'proof',
    }
    CHOICES = tuple(NAMES.items())

class DraftItem(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    item_type = models.CharField(max_length=1, choices=ItemTypes.CHOICES)
    body = models.TextField(blank=True)

    def get_absolute_url(self):
        return reverse('show-draft', args=[self.id])

    def get_item_type_title(self):
        return capfirst(self.get_item_type_display())
