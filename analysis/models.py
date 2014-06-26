from django.core.urlresolvers import reverse
from django.db import models
from analysis.helpers import compute_score
from tags.models import Category, Tag

# Models

class ItemDependency(models.Model):
    from_item = models.ForeignKey('items.FinalItem', related_name='+', db_index=True)
    to_item = models.ForeignKey('items.FinalItem', related_name='+')

    class Meta:
        db_table = 'item_deps'
        unique_together = ('from_item', 'to_item')

class ItemTag(models.Model):
    item = models.ForeignKey('items.FinalItem')
    tag = models.ForeignKey(Tag, related_name='+', db_index=True)

    class Meta:
        db_table = 'item_tags'

class DecorateCategory(models.Model):
    category = models.OneToOneField(Category)
    refer_count = models.IntegerField(null=False)
    max_points = models.FloatField(null=True)
    score = models.FloatField(null=False)

    class Meta:
        db_table = 'decorate_category'

    def save(self, *args, **kwargs):
        self.score = compute_score(self.refer_count, self.max_points)
        super().save(*args, **kwargs)

    def link_to_definitions_for(self):
        path = '/'.join(self.category.get_tag_str_list())
        return reverse('tags.views.definitions_in_category', args=[path])
