from django import template
from django.utils.safestring import mark_safe
from tags.models import Tag
from items.models import FinalItem
import items.helpers

register = template.Library()

@register.filter
def typeset_body(item):
    tag_to_category_map = {}
    if isinstance(item, FinalItem):
        for item_tag_category in item.itemtagcategory_set.all():
            tag_name = item_tag_category.tag.name
            catogory_tag_names = map(unicode, item_tag_category.category.get_tag_list())
            tag_to_category_map[tag_name] = catogory_tag_names 
    return mark_safe(items.helpers.typeset_body(item.body, tag_to_category_map))

@register.filter
def typeset_tag(tag):
    if isinstance(tag, Tag):
        tag = tag.name
    return mark_safe(items.helpers.typeset_tag(tag))

@register.filter
def typeset_tag_list(tag_list):
    return map(typeset_tag, tag_list)
