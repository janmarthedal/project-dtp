import re
from django.utils.http import urlquote, urlencode
from django.core.urlresolvers import reverse
from django.utils import crypto
import markdown

import logging
logger = logging.getLogger(__name__)

def make_html_safe(st):
    st = st.replace('<', '%lt;')
    st = st.replace('>', '%gt;')
    return st

test_body = """
First [#integer] paragraf
is started [@2222] here

We have
$$
\sum_{k=1}^n k
$$

and [number#positive integer(number theory,abc)] then we get $e^x$ the
[@ab2c] result.

"""

class BodyScanner:

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
        tags = match.group(3).split(',') if match.group(3) else []
        self._conceptRefs.append((key, '', match.group(1), match.group(2), tags))
    
    def _itemRefMatch(self, match):
        key = self._make_key()
        self._itemRefs.append((key, '', match.group(1)))
    
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
        body = re.sub(r'\[([a-zA-Z ]*)#([a-zA-Z ]+)(?:\(([a-zA-Z ]+(?:,[a-zA-Z ]+)*)\))?\]',
                      lambda match: self._conceptMatch(match), body)
        body = re.sub(r'\[@(\w+)\]',
                      lambda match: self._itemRefMatch(match), body)
        self.body = body

    def transformDisplayMath(self, func):
        self._dmaths = map(lambda p: (p[0], func(p[1])), self._dmaths)

    def transformInlineMath(self, func):
        self._imaths = map(lambda p: (p[0], func(p[1])), self._imaths)

    def transformConcepts(self, func):
        self._conceptRefs = map(lambda p: (p[0], func(p[2], p[3], p[4]), p[2], p[3], p[4]), self._conceptRefs)

    def transformItemRefs(self, func):
        self._itemRefs = map(lambda p: (p[0], func(p[2]), p[2]), self._itemRefs)

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
        

def typeset_body_paragraph(par):
    par = par.replace('\n', ' ')
    par = re.sub(r'\s{2,}', ' ', par)
    par = par.strip()
    parts = par.split('$')
    for k in range(len(parts)):
        if k % 2 == 1:
            parts[k] = '\(' + parts[k].strip() + '\)'
    return '<p>' + ''.join(parts) + '</p>'

def typeset_body2(body):
    parts = body.strip().split('$$')
    for i in range(len(parts)):
        if i % 2 == 1:
            parts[i] = '\n\[\n' + parts[i].strip() + '\n\]\n'
        else:
            parts2 = re.split(r'\s*\n\s*\n\s*', parts[i].strip())
            parts2 = map(typeset_body_paragraph, parts2)
            parts[i] = '\n'.join(parts2)
    return ''.join(parts)

def conceptMatch(match, maths, secret):
    key = 'Z%s%iZ' % (secret, len(maths))
    name = match.group(1) or match.group(2)
    # TODO: use reverse lookup
    url = '/concept/' + urlquote(match.group(2))
    if match.group(3):
        url += '?' + urlencode(dict(tags=match.group(3)))
    maths.append((key, '<a href="%s">%s</a>' % (url, name)))
    return key

def itemRefMatch(match, maths, secret):
    key = 'Z%s%iZ' % (secret, len(maths))
    final_id = match.group(1)
    url = reverse('items.views.show_final', args=[final_id])
    maths.append((key, '<a href="%s">%s</a>' % (url, final_id)))
    return key

def typeset_body(st):
    secret = crypto.get_random_string(8)
    parts = st.split('$$')
    maths = []
    for i in range(len(parts)):
        if i % 2 == 1:
            key = 'Z%s%iZ' % (secret, len(maths))
            maths.append((key, '\[' + parts[i] + '\]'))
            parts[i] = key
        else:
            parts2 = parts[i].split('$')
            for j in range(len(parts2)):
                if j % 2 == 1:
                    key = 'Z%s%iZ' % (secret, len(maths))
                    maths.append((key, '\(' + parts2[j] + '\)'))
                    parts2[j] = key
            parts[i] = ''.join(parts2)
    st = ''.join(parts)
    st = re.sub(r'\[([a-zA-Z ]*)#([a-zA-Z ]+)(?:\(([a-zA-Z ]+(?:,[a-zA-Z ]+)*)\))?\]',
                lambda match: conceptMatch(match, maths, secret), st)
    st = re.sub(r'\[@(\w+)\]',
                lambda match: itemRefMatch(match, maths, secret), st)
    st = markdown.markdown(st)
    for (old, new) in maths:
        st = st.replace(old, new)
    return st

def typeset_tag(st):
    parts = st.split('$')
    for i in range(len(parts)):
        if i % 2 == 1:
            parts[i] = '\(' + parts[i] + '\)'
    return make_html_safe(''.join(parts))

