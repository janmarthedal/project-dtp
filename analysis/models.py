from math import expm1, atan, pi
from django.core.urlresolvers import reverse
from django.db import models
from tags.models import Tag, Category
from items.models import FinalItem

import logging
logger = logging.getLogger(__name__)

class ItemDependency(models.Model):
    class Meta:
        db_table = 'item_deps'
        unique_together = ('from_item', 'to_item')
    from_item = models.ForeignKey(FinalItem, related_name='+', db_index=True)
    to_item = models.ForeignKey(FinalItem, related_name='+')

class ItemTag(models.Model):
    class Meta:
        db_table = 'item_tags'
    item = models.ForeignKey(FinalItem)
    tag = models.ForeignKey(Tag, related_name='+', db_index=True)

def compute_score(refer_count, max_points):
    max_points = max_points or 0
    importance = 0.01 - 0.99*expm1(-refer_count)
    s = 1000 if max_points > 0 else 2
    p = 2 * (s - 1) / pi * atan(0.5 * max_points * pi / (s - 1)) + 1
    return p / importance

class CategoryDefinitionUsage(models.Model):
    class Meta:
        db_table = 'category_defs'

    def save(self, *args, **kwargs):
        self.score = compute_score(self.refer_count, self.max_points)
        super(CategoryDefinitionUsage, self).save(*args, **kwargs)
    
    def link_to_definitions_for(self):
        path = '/'.join(self.category.get_tag_str_list())
        return reverse('tags.views.definitions_in_category', args=[path])

    category = models.OneToOneField(Category)
    refer_count = models.IntegerField(null=False)
    max_points = models.FloatField(null=True)
    score = models.FloatField(null=False)
