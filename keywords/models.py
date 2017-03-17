from django.db import models
from django.conf import settings

from mathitems.models import MathItem


class Keyword(models.Model):
    name = models.CharField(max_length=256, unique=True)

    class Meta:
        db_table = 'keywords'

    def __str__(self):
        return self.name


class ItemKeyword(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey(MathItem, db_index=True)
    keyword = models.ForeignKey(Keyword, db_index=True)

    class Meta:
        db_table = 'item_keyword'
        unique_together = ('item', 'keyword')
