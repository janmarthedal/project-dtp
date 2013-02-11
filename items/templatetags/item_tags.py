from django import template
from django.utils.safestring import mark_safe
import items.helpers

register = template.Library()

@register.filter
def typeset_body(value):
    return mark_safe(items.helpers.typeset_body(value))

@register.filter
def typeset_tag(value):
    return mark_safe(items.helpers.typeset_tag(value))

@register.filter
def typeset_tag_list(tag_list):
    return map(typeset_tag, tag_list)

