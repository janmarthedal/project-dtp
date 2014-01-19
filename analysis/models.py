from django.db import models
from tags.models import Tag
from items.models import FinalItem

class ItemDependency(models.Model):
    class Meta:
        db_table = 'item_deps'
        unique_together = ('from_item', 'to_item')
    from_item = models.ForeignKey(FinalItem, related_name='+', db_index=True)
    to_item   = models.ForeignKey(FinalItem, related_name='+')

class ItemTag(models.Model):
    class Meta:
        db_table = 'item_tags'
    item = models.ForeignKey(FinalItem)
    tag  = models.ForeignKey(Tag, related_name='+', db_index=True)
