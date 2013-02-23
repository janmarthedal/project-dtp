from django import template
from django.utils.safestring import mark_safe
from tags.models import Tag
import items.helpers

register = template.Library()

@register.filter
def typeset_body(value):
    return mark_safe(items.helpers.typeset_body(value))

@register.filter
def typeset_tag(tag):
    if isinstance(tag, Tag):
        tag = tag.name
    return mark_safe(items.helpers.typeset_tag(tag))

@register.filter
def typeset_tag_list(tag_list):
    return [typeset_tag(tag) for tag in tag_list]

