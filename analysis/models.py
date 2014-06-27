from django.core.urlresolvers import reverse
from django.db import models
from analysis.helpers import compute_score

# Helpers

def decorate_category(dc):
    pre_refer_count, pre_max_points = dc.refer_count, dc.max_points
    dc.refer_count = dc.category.count_references_to_this()
    dc.max_points = dc.category.best_definition_for_this()
    return dc.refer_count != pre_refer_count or dc.max_points != pre_max_points

def add_final_item_dependencies(from_item):
    to_item_list = from_item.referenced_items_in_body()
    ItemDependency.objects.filter(from_item=from_item).delete()
    ItemDependency.objects.bulk_create([ItemDependency(from_item=from_item, to_item=to_item)
                                        for to_item in to_item_list])

def update_for_categories(categories):
    for category in categories:
        try:
            cdu = DecorateCategory.objects.get(category=category)
        except DecorateCategory.DoesNotExist:
            cdu = DecorateCategory(category=category)
        if decorate_category(cdu) or cdu.pk is None:
            cdu.save()

def categories_to_redecorate(fitem):
    return fitem.categories_defined() | fitem.categories_defined()

# Models

class ItemDependency(models.Model):
    from_item = models.ForeignKey('items.FinalItem', related_name='+', db_index=True)
    to_item = models.ForeignKey('items.FinalItem', related_name='+')

    class Meta:
        db_table = 'item_deps'
        unique_together = ('from_item', 'to_item')

class ItemTag(models.Model):
    item = models.ForeignKey('items.FinalItem')
    tag = models.ForeignKey('tags.Tag', related_name='+', db_index=True)

    class Meta:
        db_table = 'item_tags'

class DecorateCategory(models.Model):
    category = models.OneToOneField('tags.Category')
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
