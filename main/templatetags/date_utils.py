from django import template
from django.utils import timezone
from django.contrib.humanize.templatetags.humanize import naturaltime

register = template.Library()


@register.filter(name='toutc')
def toutc_filter(date):
    return date.replace(tzinfo=None)


@register.filter(name='date_or_ago')
def date_or_ago_filter(date):
    now = timezone.now()
    if (now - date).days < 7:
        return naturaltime(date)
    return date.strftime('%Y-%m-%d')
