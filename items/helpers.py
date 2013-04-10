import re
import json
import markdown
from django.utils.http import urlquote, urlencode
from django.core.urlresolvers import reverse
from django.utils import crypto
from django import forms
from items.models import FinalItem
from tags.models import Tag
from tags.helpers import clean_tag, normalize_tag

import logging
logger = logging.getLogger(__name__)


class TagListField(forms.CharField):

    def __init__(self, *args, **kwargs):
        super(TagListField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(TagListField, self).clean(value)
        tag_list = filter(None, map(clean_tag, value.splitlines()))
        return tag_list


def make_html_safe(st):
    st = st.replace('<', '%lt;')
    st = st.replace('>', '%gt;')
    return st

test_body = """
First [#non-negative integer] paragraf
is started [@2222] here

We have
$$
\sum_{k=1}^n k
$$

and [number#positive integer(number $e^x$ theory,abc)] then we get $e^x$ the
[@ab2c] result.

"""

class BodyScanner:

    def __init__(self, body):
        self._secret = crypto.get_random_string(8)
        self._counter = 0
        self._dmaths = []
        self._imaths = {}
        self._conceptRefs = []
        self._itemRefs = [] 
        parts = body.split('$$')
        for i in range(len(parts)):
            if i % 2 == 1:
                parts[i] = self._add_display_maths(parts[i])
            else:
                parts2 = parts[i].split('$')
                for j in range(len(parts2)):
                    if j % 2 == 1:
                        parts2[j] = self._add_inline_maths(parts2[j])
                parts[i] = ''.join(parts2)
        body = ''.join(parts)
        body = re.sub(r'\[([0-9a-zA-Z -]*)#([0-9a-zA-Z -]+)(?:\(([0-9a-zA-Z -]+(?:,[0-9a-zA-Z -]+)*)\))?\]',
                      self._conceptMatch, body)
        body = re.sub(r'\[@(\w+)\]',
                      self._itemRefMatch, body)
        self.body = body
        self._imaths = self._imaths.items()

    def _make_key(self):
        self._counter += 1
        return 'Z%s%dZ' % (self._secret, self._counter)
    
    def _add_display_maths(self, st):
        key = self._make_key()
        self._dmaths.append((key, st))
        return key

    def _add_inline_maths(self, st):
        key = self._make_key()
        self._imaths[key] = st;
        return key

    def _prepare_tag(self, st):
        return re.sub('Z' + self._secret + r'\d+Z',
                      lambda m: '$' + self._imaths.get(m.group(0), '!') + '$',
                      clean_tag(st))
    
    def _conceptMatch(self, match):
        key = self._make_key()
        name        = match.group(1)
        primary     = self._prepare_tag(match.group(2))
        secondaries = map(self._prepare_tag, match.group(3).split(',')) if match.group(3) else []
        self._conceptRefs.append((key, '', name, primary, secondaries))
        return key
    
    def _itemRefMatch(self, match):
        key = self._make_key()
        self._itemRefs.append((key, '', match.group(1)))
        return key
    
    def transformDisplayMath(self, func):
        self._dmaths = map(lambda p: (p[0], func(p[1])), self._dmaths)

    def transformInlineMath(self, func):
        self._imaths = map(lambda p: (p[0], func(p[1])), self._imaths)

    def transformConcepts(self, func):
        self._conceptRefs = map(lambda p: (p[0], func(p[2], p[3], p[4]), p[2], p[3], p[4]), self._conceptRefs)

    def transformItemRefs(self, func):
        self._itemRefs = map(lambda p: (p[0], func(p[2]), p[2]), self._itemRefs)

    def getItemRefList(self):
        return [p[2] for p in self._itemRefs]

    def getConceptList(self):
        return [(p[3], p[4]) for p in self._conceptRefs]

    def assemble(self):
        st = self.body
        for (key, value) in self._dmaths:
            st = st.replace(key, value)
        for (key, value) in self._imaths:
            st = st.replace(key, value)
        for (key, value, _1, _2, _3) in self._conceptRefs:
            st = st.replace(key, value)
        for (key, value, _1) in self._itemRefs:
            st = st.replace(key, value)
        return st
        

def typesetConcept(name, primary, secondaries):
    name = name or primary
    url = reverse('items.definitions.views.concept_search', args=[urlquote(primary)])
    if secondaries:
        url += '?' + urlencode(dict(tags=','.join(secondaries)))
    return '<a href="%s">%s</a>' % (url, typeset_tag(name))

def typesetItemRef(final_id):
    url = reverse('items.views.show_final', args=[final_id])
    return '<a href="%s">%s</a>' % (url, final_id)

def typeset_body(st):
    bs = BodyScanner(st)
    bs.body = markdown.markdown(bs.body)
    bs.transformDisplayMath(lambda st: '\\[' + st + '\\]')
    bs.transformInlineMath(lambda st: '\\(' + st + '\\)')
    bs.transformConcepts(typesetConcept)
    bs.transformItemRefs(typesetItemRef)
    return bs.assemble()

def typeset_tag(st):
    parts = st.split('$')
    for i in range(len(parts)):
        if i % 2 == 1:
            parts[i] = '\(' + parts[i] + '\)'
    return make_html_safe(''.join(parts))


class TagSearchForm(forms.Form):
    includetags = TagListField(widget=forms.Textarea(attrs={'class': 'tags'}), required=False)
    excludetags = TagListField(widget=forms.Textarea(attrs={'class': 'tags'}), required=False)


def tag_names_to_tag_objects(tag_names):
    found = []
    not_found = []
    tag_names = set(map(normalize_tag, tag_names)) - set([''])
    for tag_name in tag_names:
        try:
            tag = Tag.objects.get(normalized=tag_name)
            found.append(tag)
        except Tag.DoesNotExist:
            not_found.append(tag_name)
    return (found, not_found)

def item_search_to_json(itemtype, include_tag_names=[], exclude_tag_names=[], offset=0, limit=5):
    query = FinalItem.objects.filter(status='F')
    if itemtype:
        query = query.filter(itemtype=itemtype) 
    (include_tags, not_found) = tag_names_to_tag_objects(include_tag_names)
    if not not_found:
        (exclude_tags, not_found) = tag_names_to_tag_objects(exclude_tag_names)
        for tag in include_tags:
            query = query.filter(finalitemtag__tag=tag)
        for tag in exclude_tags:
            query = query.exclude(finalitemtag__tag=tag)
    query = query.order_by('-created_at')
    items = query[offset:(offset+limit+1)]
    result = {
              'meta': {
                       'offset':   offset,
                       'count':    min(len(items), limit),
                       'has_more': len(items) > limit
                       },
              'items': [{
                         'id':   item.final_id,
                         'type': item.itemtype,
                         'tags': {
                                  'primary':   [t.name for t in item.primary_tags],
                                  'secondary': [t.name for t in item.secondary_tags]
                                  }
                         } for item in items[:limit]]
              }
    return json.dumps(result)
