import re
import markdown
from django.http import Http404
from django.core.urlresolvers import reverse
from django.utils import crypto
from django.utils.http import urlquote
from drafts.models import DraftItem
from items.models import FinalItem
from main.helpers import json_encode
from tags.models import Tag
from tags.helpers import normalize_tag

import logging
logger = logging.getLogger(__name__)

def make_html_safe(st):
    st = st.replace('<', '%lt;')
    st = st.replace('>', '%gt;')
    return st


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
        body = re.sub(r'\[([^#\]]*)#([\w -]+)\]', self._conceptMatch, body)
        body = re.sub(r'\[([^@\]]*)@(\w+)\]', self._itemRefMatch, body)
        body = body.replace("[", "&#91;").replace("]", "&#93;").replace("<", "&lt;").replace(">", "&gt;");
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

    def transformDisplayMath(self, func):
        self._dmaths = map(lambda p: (p[0], func(p[1])), self._dmaths)

    def transformInlineMath(self, func):
        self._imaths = map(lambda p: (p[0], func(p[1])), self._imaths)

    def transformConcepts(self, func):
        self._conceptRefs = map(lambda p: (p[0], func(p[2], p[3]), p[2], p[3]), self._conceptRefs)

    def transformItemRefs(self, func):
        self._itemRefs = map(lambda p: (p[0], func(p[2], p[3]), p[2], p[3]), self._itemRefs)

    def getItemRefSet(self):
        return [p[2] for p in self._itemRefs]

    def getConceptSet(self):
        return [p[3] for p in self._conceptRefs]

    def assemble(self):
        st = self.body
        for (key, value, _1, _2) in self._conceptRefs:
            st = st.replace(key, value)
        for (key, value, _1, _2) in self._itemRefs:
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
        href = reverse('tags.views.show', args=[path]) + '?type=d'
        return '<a href="%s"><i>%s</i></a>' % (href, link_text)
    except KeyError:
        return '<a href="#" rel="tooltip" data-original-title="tag: %s"><i>%s</i></a>' % (tag_name, link_text)


def typesetItemRef(text, item_id):
    link_text = make_html_safe(text or item_id)
    url = reverse('items.views.show_final', args=[item_id])
    return '<a href="%s"><b>%s</b></a>' % (url, link_text)


def typeset_body(st, tag_to_category_map):
    bs = BodyScanner(st)
    bs.body = markdown.markdown(bs.body)
    bs.transformDisplayMath(lambda st: '\\[' + st + '\\]')
    bs.transformInlineMath(lambda st: '\\(' + st + '\\)')
    bs.transformConcepts(lambda text, tag_name: typesetConcept(text, tag_name, tag_to_category_map))
    bs.transformItemRefs(typesetItemRef)
    return bs.assemble()


def typeset_tag(st):
    parts = st.split('$')
    for i in range(len(parts)):
        if i % 2 == 1:
            parts[i] = '\(' + parts[i] + '\)'
    return make_html_safe(''.join(parts))


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


def _extract_draft_item_attributes(item):
    result = {
        'id':          item.pk,
        'item_link':   reverse('drafts.views.show', args=[item.pk]),
        'type':        item.itemtype,
        'author':      item.created_by.get_full_name(),
        'author_link': reverse('users.views.profile', args=[item.created_by.get_username()]),
        'timestamp':   str(item.modified_at),
        'categories':  {
            'primary':   item.primary_categories,
            'secondary': item.secondary_categories
        }
    }
    if item.parent:
        result.update(parent = { 'id': item.parent.final_id, 'type': item.parent.itemtype })
    return result


def _extract_final_item_attributes(item):
    result = {
        'id':          item.final_id,
        'item_link':   reverse('items.views.show_final', args=[item.final_id]),
        'type':        item.itemtype,
        'author':      item.created_by.get_full_name(),
        'author_link': reverse('users.views.profile', args=[item.created_by.get_username()]),
        'timestamp':   str(item.created_at),
        'categories':  {
            'primary':   item.primary_categories,
            'secondary': item.secondary_categories
        }
    }
    if item.parent:
        result.update(parent = { 'id': item.parent.final_id, 'type': item.parent.itemtype })
    return result


def item_search_to_json(itemtype=None, parent=None, include_tag_names=[], exclude_tag_names=[], status='F', offset=0, limit=5, user=None):
    if itemtype and itemtype not in ['D', 'T', 'P']:
        raise Http404
    if status == 'F':
        query = FinalItem.objects.filter(status='F')
    elif (status == 'R') or (user and status == 'D'):
        query = DraftItem.objects.filter(status=status)
    else:
        raise Http404

    if itemtype:
        query = query.filter(itemtype=itemtype)
    if parent:
        query = query.filter(parent__final_id=parent)
    if user:
        query = query.filter(created_by=user)
    (include_tags, not_found) = tag_names_to_tag_objects(include_tag_names)
    if not not_found:
        (exclude_tags, not_found) = tag_names_to_tag_objects(exclude_tag_names)
        for tag in include_tags:
            query = query.filter(itemtag__tag=tag)
        for tag in exclude_tags:
            query = query.exclude(itemtag__tag=tag)
    if status == 'F':
        query = query.order_by('-created_at')
    else:
        query = query.order_by('-modified_at')
    items = query[offset:(offset+limit+1)]
    result = { 'meta': { 'offset':   offset,
                         'count':    min(len(items), limit),
                         'has_more': len(items) > limit }}
    if status == 'F':
        result['items'] = [_extract_final_item_attributes(item) for item in items[:limit]]
    else:
        result['items'] = [_extract_draft_item_attributes(item) for item in items[:limit]]
    return json_encode(result)
