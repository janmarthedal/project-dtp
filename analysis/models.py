from django.db import models
from tags.models import Tag
from items.models import FinalItem

import logging
logger = logging.getLogger(__name__)

class ItemDependency(models.Model):
    class Meta:
        db_table = 'item_deps'
        unique_together = ('from_item', 'to_item')
    from_item = models.ForeignKey(FinalItem, related_name='+', db_index=True)
    to_item   = models.ForeignKey(FinalItem, related_name='+')

class TagCount(models.Model):
    class Meta:
        db_table = 'tag_count'
    tag = models.OneToOneField(Tag, primary_key=True)
    count = models.IntegerField(db_index=True)
