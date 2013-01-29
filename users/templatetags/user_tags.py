from django import template

register = template.Library()

@register.filter
def datetime_user(stamp, user):
    return stamp.replace(microsecond=0).isoformat(' ')

