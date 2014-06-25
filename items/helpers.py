import json
import markdown
import re
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render
from django.template import Context
from django.template.loader import get_template, render_to_string
from django.utils import crypto
from django.utils.http import urlquote
from drafts.models import DraftItem
from items.models import FinalItem
from main.badrequest import BadRequest
from main.helpers import init_context, make_get_url
from media.models import MediaItem
from tags.models import Category

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

def publishIssues(draft_item):
    issues = []
    if not draft_item.body.strip():
        issues.append('No contents')
    bs = BodyScanner(draft_item.body)
    for itemref_id in bs.getItemRefSet():
        if not FinalItem.objects.filter(final_id=itemref_id, status='F').exists():
            issues.append("Reference to non-existing item '%s'" % itemref_id)
    for media_id in bs.getMediaRefSet():
        if not MediaItem.objects.filter(entry__public_id=media_id, itemtype='O').exists():
            issues.append("Reference to non-existing media '%s'" % media_id)
    return issues


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

def prepare_list_items(queryset, page_size, page_num=1):
    offset = (page_num - 1) * page_size
    item_list = queryset[offset:(offset + page_size + 1)]
    return (item_list[0:page_size], len(item_list) > page_size)


class PagedSearch(object):
    defaults = []

    def __init__(self, request=None, **kwargs):
        self.search_data = {}
        if request:
            self.update_from_request(request)
        self.search_data.update(kwargs)

    def update_from_request(self, request):
        self.search_data.update(page=request_get_int(request, 'page', 1, lambda v: v >= 1))

    def make_search(self, page_size):
        current_url = self.get_url()
        page = self.search_data.get('page') or 1
        queryset = self.get_queryset()
        items, more = prepare_list_items(queryset, page_size, page)
        pagedata = {'rendered': '', 'prev_data_url': '', 'next_data_url': ''}
        if items:
            pagedata['rendered'] = render_to_string(self.template_name, {'items': items, 'current_url': current_url})
        if page > 1:
            pagedata['prev_data_url'] = self.get_url(page=page-1)
        if more:
            pagedata['next_data_url'] = self.get_url(page=page+1)
        return pagedata

    def get_count(self):
        return self.get_queryset().count()

    def get_url(self, **changed):
        url = self.get_base_url()
        defaults = set(self.defaults) | {('page', 1)}
        data = dict(self.search_data, **changed)
        params = dict(kv for kv in data.items() if kv not in defaults)
        return make_get_url(url, params)


class ItemPagedSearch(PagedSearch):
    template_name = 'include/item_list_items.html'
    defaults = [('status', 'F')]

    def __init__(self, user=None, pricat=None, **kwargs):
        self.user = user
        self.pricat = pricat
        super(ItemPagedSearch, self).__init__(**kwargs)

    def get_queryset(self):
        drafts = self.search_data.get('status') in ['R', 'D']
        queryset = DraftItem.objects if drafts else FinalItem.objects
        if self.search_data.get('status'):
            queryset = queryset.filter(status=self.search_data['status'])
        if self.search_data.get('type'):
            queryset = queryset.filter(itemtype=self.search_data['type'])
        if self.user:
            queryset = queryset.filter(created_by=self.user)
        if self.search_data.get('parent'):
            queryset = queryset.filter(parent__final_id=self.search_data['parent'])
        if self.pricat:
            if drafts:
                if self.pricat >= 0:
                    queryset = queryset.filter(draftitemcategory__primary=True, draftitemcategory__category__id=self.pricat)
                else:
                    queryset = queryset.filter(draftitemcategory__primary=True, draftitemcategory__category=None)
            else:
                if self.pricat >= 0:
                    queryset = queryset.filter(finalitemcategory__primary=True, finalitemcategory__category__id=self.pricat)
                else:
                    queryset = queryset.filter(finalitemcategory__primary=True, finalitemcategory__category=None)
        return queryset.order_by('-created_at')

    def get_base_url(self):
        if self.user:
            url = reverse('users.views.items', args=[self.user.pk])
        elif self.pricat:
            tags = []
            if self.pricat >= 0:
                try:
                    category = Category.objects.get(pk=self.pricat)
                except Category.DoesNotExist:
                    raise BadRequest
                tags = map(str, category.get_tag_list())
            reqpath = '/'.join(tags)
            if self.search_data['type'] == 'D':
                url = reverse('tags.views.definitions_in_category', args=[reqpath])
            elif self.search_data['type'] == 'T':
                url = reverse('tags.views.theorems_in_category', args=[reqpath])
            else:
                raise BadRequest
        else:
            url = reverse('items.views.search')
        return url

    def update_from_request(self, request):
        #self.pricat = request_get_int(request, 'pricat')
        self.search_data.update({
            'type': request_get_string(request, 'type', None, lambda v: v in [None, 'D', 'T', 'P']),
            'status': request_get_string(request, 'status', 'F', lambda v: v in ['F', 'R', 'D']),
            'parent': request.GET.get('parent'),
        })
        super().update_from_request(request)

    def change_search_url(self, **kwargs):
        cururl = self.get_url()
        newurl = self.get_url(**kwargs)
        return {'link': newurl, 'changed': cururl != newurl}

    def render(self, request):
        itempage = self.make_search(20)

        if request.GET.get('partial') is not None:
            return HttpResponse(json.dumps(itempage), content_type="application/json")
        else:
            self.search_data['page'] = None
            links = {
                'type': {
                    'D': self.change_search_url(type='D'),
                    'T': self.change_search_url(type='T'),
                },
                'status': {
                    'F': self.change_search_url(status='F'),
                    'R': self.change_search_url(status='R'),
                }
            }
            if not self.pricat:
                links['type'].update({
                    'all': self.change_search_url(type=None),
                    'P': self.change_search_url(type='P'),
                })
            if self.user == request.user:
                links['status']['D'] = self.change_search_url(status='D')
            c = init_context('search', itempage=itempage, links=links, search_user=self.user)
            if self.search_data.get('parent'):
                try:
                    c.update(parent=FinalItem.objects.get(final_id=self.search_data['parent']))
                except FinalItem.DoesNotExist:
                    raise BadRequest
            if self.pricat:
                c['pricat_text'] = {'D': 'Definitions in', 'T': 'Theorems for'}[self.search_data['type']]
                try:
                    c['category'] = Category.objects.get(pk=self.pricat)
                except Category.DoesNotExist:
                    raise BadRequest
            return render(request, 'items/search.html', c)

def get_primary_text(type_key):
    vals = {'D': 'Terms defined', 'T': 'Name(s) for theorem'}
    return vals.get(type_key)
