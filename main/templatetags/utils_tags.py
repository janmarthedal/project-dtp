from django import template
from django.utils.safestring import mark_safe
from main.helpers import json_encode
from django.utils import timezone

register = template.Library()

@register.filter
def to_json(obj):
    return mark_safe(json_encode(obj))

@register.filter
def timestamp(time, user=None):
    now = timezone.now()
    elapsed = (now - time) // timezone.timedelta(seconds=1)  # seconds
    if elapsed < 60:
        return 'just now'
    elapsed //= 60                                           # minutes
    if elapsed < 60:
        return '{} minutes ago'.format(elapsed)
    elapsed //= 60                                           # hours
    if elapsed < 24:
        return '{} hours ago'.format(elapsed)
    elapsed //= 24                                           # days
    if elapsed < 7:
        return '{} days ago'.format(elapsed)
    return 'on {}'.format(time.date().isoformat())
