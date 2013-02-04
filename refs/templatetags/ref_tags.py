from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
import items.helpers

register = template.Library()

@register.filter
def typeset_refnode(refnode):
    attrs = {}
    for a in refnode.attributes.all():
        field = escape(a.field.name)
        value = escape(a.value)
        if field in attrs:
            attrs[field].append(value)
        else:
            attrs[field] = [value]
    ret = ''
    if 'author' in attrs:
        authors = attrs.pop('author')
        if len(authors) == 1:
            ret += authors[0]
        elif len(authors) == 2:
            ret += authors[0] + ' and ' + authors[1]
        else:
            ret += ', '.join(authors[0:-2]) + ', and ' + authors[-1]
        ret += '. '
    if len(attrs.get('title', [])) == 1:
        ret += '<i>' + attrs.pop('title')[0] + '</i>. '
    if len(attrs) > 0:
        elems = []
        for field, values in attrs.iteritems():
            for value in values:
                elems.append(field + ': ' + value)
        ret += '(' + ', '.join(elems) + ')'
    return mark_safe(ret)

