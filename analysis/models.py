from django.core.urlresolvers import reverse
from django.db import models
import analysis.helpers
from items.models import FinalItem
from tags.models import Category, Tag

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

class DecorateCategory(models.Model):
    class Meta:
        db_table = 'decorate_category'

    def save(self, *args, **kwargs):
        self.score = analysis.helpers.compute_score(self.refer_count, self.max_points)
        super().save(*args, **kwargs)

    def link_to_definitions_for(self):
        path = '/'.join(self.category.get_tag_str_list())
        return reverse('tags.views.definitions_in_category', args=[path])

    category = models.OneToOneField(Category)
    refer_count = models.IntegerField(null=False)
    max_points = models.FloatField(null=True)
    score = models.FloatField(null=False)
