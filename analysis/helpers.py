from math import expm1, atan, pi
from django.core.management.base import CommandError
from django.db.models import Max
import analysis.models
import items.models
import tags.models

def add_final_item_dependencies(from_item):
    bs = items.helpers.BodyScanner(from_item.body)
    try:
        to_item_list = [items.models.FinalItem.objects.get(final_id=itemref_id) for itemref_id in bs.getItemRefSet()]
    except ValueError:
        raise CommandError("add_final_item_dependencies: illegal item name '%s'" % itemref_id)
    except items.models.FinalItem.DoesNotExist:
        raise CommandError("add_final_item_dependencies: non-existent item '%s'" % str(itemref_id))
    analysis.models.ItemDependency.objects.filter(from_item=from_item).delete()
    analysis.models.ItemDependency.objects.bulk_create([analysis.models.ItemDependency(from_item=from_item, to_item=to_item)
                                                        for to_item in to_item_list])

def check_final_item_tag_categories(fitem):
    bs = items.helpers.BodyScanner(fitem.body)

    tags_in_item = set([tags.models.Tag.objects.fetch(tag_name) for tag_name in bs.getConceptSet()])
    tags_in_db = set([itc.tag for itc in fitem.itemtagcategory_set.all()])
    tags_to_remove = tags_in_db - tags_in_item
    tags_to_add = tags_in_item - tags_in_db

    for tag in tags_to_remove:
        items.models.ItemTagCategory.objects.filter(item=fitem, tag=tag).delete()

    for tag in tags_to_add:
        category = tags.models.Category.objects.default_category_for_tag(tag)
        items.models.ItemTagCategory.objects.create(item=fitem, tag=tag, category=category)

    return len(tags_to_add), len(tags_to_remove)

def compute_score(refer_count, max_points):
    max_points = max_points or 0
    importance = 0.01 - 0.99*expm1(-refer_count)
    s = 1000 if max_points > 0 else 2
    p = 2 * (s - 1) / pi * atan(0.5 * max_points * pi / (s - 1)) + 1
    return p / importance

def queryset_generator(queryset):
    items = queryset.order_by('pk')[:100]
    while items:
        latest_pk = items[len(items) - 1].pk
        for item in items:
            yield item
        items = queryset.filter(pk__gt=latest_pk).order_by('pk')[:100]

def decorate_category(dc):
    pre_refer_count, pre_max_points = dc.refer_count, dc.max_points
    dc.refer_count = items.models.FinalItem.objects.filter(status='F', itemtagcategory__category=dc.category).count()
    dc.max_points = items.models.FinalItem.objects.filter(status='F', itemtype='D', finalitemcategory__primary=True,
                                                          finalitemcategory__category=dc.category).aggregate(Max('points'))['points__max']
    return dc.refer_count != pre_refer_count or dc.max_points != pre_max_points

def update_for_categories(categories):
    for category in categories:
        try:
            cdu = analysis.models.DecorateCategory.objects.get(category=category)
        except analysis.models.DecorateCategory.DoesNotExist:
            cdu = analysis.models.DecorateCategory(category=category)
        if decorate_category(cdu) or cdu.pk is None:
            cdu.save()

def categories_to_redecorate(fitem):
    return fitem.categories_defined() | fitem.categories_defined()
