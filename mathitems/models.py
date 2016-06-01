from django.conf import settings
#from django.core.urlresolvers import reverse
from django.db import models

from mathitems.itemtypes import ItemTypes


class MathItemItem(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    item_type = models.CharField(max_length=1, choices=ItemTypes.CHOICES)
    body = models.TextField()

    def __str__(self):
        return '{} {}'.format(self.get_item_type_display(), self.id)


class Equation(models.Model):
    class Meta:
        unique_together = ['format', 'math']
    format = models.CharField(max_length=10)  # inline-TeX, TeX
    math = models.TextField()
    html = models.TextField()


class Concept(models.Model):
    name = models.CharField(max_length=64, unique=True)
