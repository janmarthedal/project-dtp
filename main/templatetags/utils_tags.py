from django import template
from django.utils.safestring import mark_safe
from main.helpers import json_encode

#import logging
#logger = logging.getLogger(__name__)

register = template.Library()

@register.filter
def to_json(obj):
    return mark_safe(json_encode(obj))
