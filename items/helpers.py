import re
from django.utils.http import urlquote, urlencode
from django.core.urlresolvers import reverse
from django.utils import crypto
import markdown
from tags.helpers import clean_tag

import logging
logger = logging.getLogger(__name__)

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

and [number#positive integer(number theory,abc)] then we get $e^x$ the
[@ab2c] result.

"""

class BodyScanner:

    def __init__(self, body):
        self._secret = crypto.get_random_string(8)
        self._counter = 0
        self._dmaths = []
        self._imaths = []
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
        body = re.sub(r'\[([a-zA-Z -]*)#([a-zA-Z -]+)(?:\(([a-zA-Z -]+(?:,[a-zA-Z -]+)*)\))?\]',
                      self._conceptMatch, body)
        body = re.sub(r'\[@(\w+)\]',
                      self._itemRefMatch, body)
        self.body = body

    def _make_key(self):
        self._counter += 1
        return 'Z%s%dZ' % (self._secret, self._counter)
    
    def _add_display_maths(self, st):
        key = self._make_key()
        self._dmaths.append((key, st))
        return key
    
    def _add_inline_maths(self, st):
        key = self._make_key()
        self._imaths.append((key, st))
        return key
    
    def _conceptMatch(self, match):
        key = self._make_key()
        name        = match.group(1)
        primary     = clean_tag(match.group(2))
        secondaries = map(clean_tag, match.group(3).split(',')) if match.group(3) else []
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
    # TODO: use reverse lookup
    url = reverse('definitions.views.concept_search', args=[primary])
    if secondaries:
        url += '?' + urlencode(dict(tags=','.join(secondaries)))
    return '<a href="%s">%s</a>' % (url, name)

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

