import markdown
import re
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import get_template
from django.utils import crypto
from django.utils.http import urlquote
from main.badrequest import BadRequest
from media.models import MediaItem

import logging
logger = logging.getLogger(__name__)


def make_html_safe(st):
    st = st.replace('<', '&lt;')
    st = st.replace('>', '&gt;')
    return st


class BodyScanner:

    def __init__(self, body):
        self._secret = crypto.get_random_string(8)
        self._counter = 0
        self._dmaths = []
        self._imaths = {}
        self._conceptRefs = []
        self._itemRefs = []
        self._mediaRefs = []
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
        body = re.sub(r'\[([^#\]]*)#([\w -]+)\]', self._conceptMatch, body)
        body = re.sub(r'\[([^@\]]*)@(\w+)\]', self._itemRefMatch, body)
        body = re.sub(r'\s*\[([^!\]]*)!(\w+)\]\s*', self._mediaRefMatch, body)
        body = body.replace('[', '&#91;').replace(']', '&#93;')
        body = body.replace('<', '&lt;').replace('>', '&gt;')
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
        self._imaths[key] = st
        return key

    def _conceptMatch(self, match):
        key = self._make_key()
        name = match.group(1)
        tag = match.group(2)
        self._conceptRefs.append((key, '', name, tag))
        return key

    def _itemRefMatch(self, match):
        key = self._make_key()
        name = match.group(1)
        item_id = match.group(2)
        self._itemRefs.append((key, '', name, item_id))
        return key

    def _mediaRefMatch(self, match):
        key = self._make_key()
        name = match.group(1)
        media_id = match.group(2)
        self._mediaRefs.append((key, '', name, media_id))
        return '\n\n' + key + '\n\n'

    def transformDisplayMath(self, func):
        self._dmaths = map(lambda p: (p[0], func(p[1])), self._dmaths)

    def transformInlineMath(self, func):
        self._imaths = map(lambda p: (p[0], func(p[1])), self._imaths)

    def transformConcepts(self, func):
        self._conceptRefs = map(lambda p: (p[0], func(p[2], p[3]), p[2], p[3]), self._conceptRefs)

    def transformItemRefs(self, func):
        self._itemRefs = map(lambda p: (p[0], func(p[2], p[3]), p[2], p[3]), self._itemRefs)

    def transformMediaRefs(self, func):
        self._mediaRefs = map(lambda p: (p[0], func(p[2], p[3]), p[2], p[3]), self._mediaRefs)

    def getConceptSet(self):
        return set([p[3] for p in self._conceptRefs])

    def getItemRefSet(self):
        return set([p[3] for p in self._itemRefs])

    def getMediaRefSet(self):
        return set([p[3] for p in self._mediaRefs])

    def assemble(self):
        st = self.body
        for (key, value, _1, _2) in self._conceptRefs:
            st = st.replace(key, value)
        for (key, value, _1, _2) in self._itemRefs:
            st = st.replace(key, value)
        for (key, value, _1, _2) in self._mediaRefs:
            st = st.replace(key, value)
        for (key, value) in self._dmaths:
            st = st.replace(key, value)
        for (key, value) in self._imaths:
            st = st.replace(key, value)
        return st

def typesetConcept(text, tag_name, tag_to_category_map):
    link_text = typeset_tag(text or tag_name)
    try:
        tag_list = tag_to_category_map[tag_name]
        path = '/'.join(map(lambda tag: urlquote(tag, safe=''), tag_list))
        href = reverse('tags.views.definitions_in_category', args=[path])
        return '<a href="%s"><i>%s</i></a>' % (href, link_text)
    except KeyError:
        return '<a href="#" rel="tooltip" data-original-title="tag: %s"><i>%s</i></a>' % (tag_name, link_text)

def typesetItemRef(text, item_id):
    link_text = make_html_safe(text or item_id)
    url = reverse('items.views.show_final', args=[item_id])
    return '<a href="%s"><b>%s</b></a>' % (url, link_text)

def typesetMediaRef(text, media_id):
    c = dict(name=media_id, description=text)
    try:
        item = MediaItem.objects.get(entry__public_id=media_id, itemtype='O')
        c.update(link=settings.MEDIA_URL + item.path)
    except MediaItem.DoesNotExist:
        c.update(error='Media does not exist')
    template = get_template('items/item_image.html')
    return template.render(Context(c))

def typeset_body(st, tag_to_category_map):
    bs = BodyScanner(st)
    bs.body = markdown.markdown(bs.body)
    bs.transformDisplayMath(lambda st: '\\[' + st + '\\]')
    bs.transformInlineMath(lambda st: '\\(' + st + '\\)')
    bs.transformConcepts(lambda text, tag_name: typesetConcept(text, tag_name, tag_to_category_map))
    bs.transformItemRefs(typesetItemRef)
    bs.transformMediaRefs(typesetMediaRef)
    return bs.assemble()

def typeset_tag(st):
    parts = st.split('$')
    for i in range(len(parts)):
        if i % 2 == 1:
            parts[i] = '\(' + parts[i] + '\)'
    return make_html_safe(''.join(parts))

def request_get_int(request, key, default=None, validator=None):
    try:
        value = int(request.GET[key]) if key in request.GET else default
    except (ValueError, TypeError):
        raise BadRequest
    if validator and not validator(value):
        raise BadRequest
    return value

def request_get_string(request, key, default, validator):
    value = request.GET.get(key, default)
    if not validator(value):
        raise BadRequest
    return value

def get_primary_text(type_key):
    vals = {'D': 'Terms defined', 'T': 'Name(s) for theorem'}
    return vals.get(type_key)
