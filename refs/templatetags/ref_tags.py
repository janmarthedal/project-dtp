from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
import items.helpers

register = template.Library()

@register.filter
def typeset_refnode(refnode):
    ret = ''
    authors = [escape(a.name) for a in refnode.authors.all()]
    if authors:
        if len(authors) == 1:
            ret += authors[0]
        elif len(authors) == 2:
            ret += authors[0] + ' and ' + authors[1]
        else:
            ret += ', '.join(authors[0:-2]) + ', and ' + authors[-1]
        ret += '. '
    if refnode.title:
        ret += '<i>' + escape(refnode.title) + '</i>. '
    elems = []
    for field in ['publisher', 'edition', 'series', 'year', 'isbn10', 'isbn13', 'extra']:
        if refnode.__dict__[field]:
            elems.append(field + ': ' + escape(refnode.__dict__[field]))
    if elems:
        ret += '(' + ', '.join(elems) + ')'
    return mark_safe(ret)

