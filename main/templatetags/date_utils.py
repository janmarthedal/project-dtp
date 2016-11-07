from django import template

register = template.Library()

@register.filter(name='toutc')
def toutc(date):
    return date.replace(tzinfo=None)
