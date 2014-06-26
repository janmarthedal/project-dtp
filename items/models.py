import json
import string
from django.conf import settings
from django.core.management.base import CommandError
from django.core.urlresolvers import reverse
from django.db import models, IntegrityError
from django.db.models import Max, Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import get_random_string
from analysis.models import ItemDependency, DecorateCategory
from drafts.models import BaseItem, DraftItem
from items.helpers import BodyScanner, request_get_int, request_get_string
from main.badrequest import BadRequest
from main.helpers import init_context, make_get_url
from sources.models import ValidationBase
from tags.models import Category, Tag

import logging
logger = logging.getLogger(__name__)

# Helpers

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

def check_final_item_tag_categories(fitem):
    bs = BodyScanner(fitem.body)

    tags_in_item = set([Tag.objects.fetch(tag_name) for tag_name in bs.getConceptSet()])
    tags_in_db = set([itc.tag for itc in fitem.itemtagcategory_set.all()])
    tags_to_remove = tags_in_db - tags_in_item
    tags_to_add = tags_in_item - tags_in_db

    for tag in tags_to_remove:
        ItemTagCategory.objects.filter(item=fitem, tag=tag).delete()

    for tag in tags_to_add:
        category = Category.objects.default_category_for_tag(tag)
        ItemTagCategory.objects.create(item=fitem, tag=tag, category=category)

    return len(tags_to_add), len(tags_to_remove)

def add_final_item_dependencies(from_item):
    bs = BodyScanner(from_item.body)
    try:
        to_item_list = [FinalItem.objects.get(final_id=itemref_id) for itemref_id in bs.getItemRefSet()]
    except ValueError:
        raise CommandError("add_final_item_dependencies: illegal item name '%s'" % itemref_id)
    except FinalItem.DoesNotExist:
        raise CommandError("add_final_item_dependencies: non-existent item '%s'" % str(itemref_id))
    ItemDependency.objects.filter(from_item=from_item).delete()
    ItemDependency.objects.bulk_create([ItemDependency(from_item=from_item, to_item=to_item)
                                        for to_item in to_item_list])

def decorate_category(dc):
    pre_refer_count, pre_max_points = dc.refer_count, dc.max_points
    dc.refer_count = FinalItem.objects.filter(status='F', itemtagcategory__category=dc.category).count()
    dc.max_points = FinalItem.objects.filter(status='F', itemtype='D', finalitemcategory__primary=True,
                                             finalitemcategory__category=dc.category).aggregate(Max('points'))['points__max']
    return dc.refer_count != pre_refer_count or dc.max_points != pre_max_points

def update_for_categories(categories):
    for category in categories:
        try:
            cdu = DecorateCategory.objects.get(category=category)
        except DecorateCategory.DoesNotExist:
            cdu = DecorateCategory(category=category)
        if decorate_category(cdu) or cdu.pk is None:
            cdu.save()

def categories_to_redecorate(fitem):
    return fitem.categories_defined() | fitem.categories_defined()

def pre_update_finalitem(fitem):
    return categories_to_redecorate(fitem)

def post_update_finalitem(fitem, categories_before):
    categories_after = categories_to_redecorate(fitem)
    update_for_categories(categories_before | categories_after)

def post_create_finalitem(fitem):
    add_final_item_dependencies(fitem)
    check_final_item_tag_categories(fitem)
    update_for_categories(categories_to_redecorate(fitem))

def post_update_finalitem_points(fitem):
    update_for_categories(fitem.categories_defined())

# Managers

FINAL_NAME_CHARS = string.digits
FINAL_NAME_MIN_LENGTH = 4
FINAL_NAME_MAX_LENGTH = 10

class FinalItemManager(models.Manager):

    def add_item(self, draft_item):
        item = FinalItem(itemtype = draft_item.itemtype,
                         status = 'F',
                         created_by = draft_item.created_by,
                         modified_by = draft_item.created_by,
                         body = draft_item.body,
                         parent = draft_item.parent)
        for length in range(FINAL_NAME_MIN_LENGTH, FINAL_NAME_MAX_LENGTH):
            item.final_id = item.itemtype + get_random_string(length, FINAL_NAME_CHARS)
            try:
                item.save()
                for itemcat in draft_item.draftitemcategory_set.all():
                    FinalItemCategory.objects.create(item=item, category=itemcat.category,
                                                     primary=itemcat.primary)
                for validation in draft_item.draftvalidation_set.all():
                    ItemValidation.objects.create(item=item, created_by=validation.created_by,
                                                  source=validation.source, location=validation.location)
                return item
            except IntegrityError:
                pass
        raise Exception('FinalItemManager.add_item')

# Models

class FinalItem(BaseItem):

    class Meta:
        db_table = 'final_items'

    objects = FinalItemManager()

    STATUS_CHOICES = (
        ('F', 'published'),
        ('S', 'suspended'),
        ('B', 'broken')
    )

    final_id = models.CharField(max_length=FINAL_NAME_MAX_LENGTH, unique=True, db_index=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='F')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', db_index=False)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', db_index=False)
    categories = models.ManyToManyField(Category, through='FinalItemCategory')
    points = models.FloatField(default=0, null=False)

    def __str__(self):
        return ''.join([self.get_itemtype_display().capitalize(), ' ', self.final_id])

    def _get_item_category_set(self):
        return self.finalitemcategory_set.all()

    def get_tag_category_associations(self):
        return list(self.itemtagcategory_set.all())

    def _add_category_list(self, categories, is_primary):
        for tag_list in categories:
            category = Category.objects.from_tag_list(tag_list)
            FinalItemCategory.objects.create(item=self, category=category, primary=is_primary)

    def set_item_tag_categories(self, tag_category_list):
        for tag_category in tag_category_list:
            tag = Tag.objects.fetch(tag_category['tag'])
            category = tag_category['category']
            if not isinstance(category, Category):
                category = Category.objects.from_tag_list(category)
            ItemTagCategory.objects.create(item=self, tag=tag, category=category)

    def update(self, user, primary_categories, secondary_categories, tag_category_list):
        pre_update_data = pre_update_finalitem(self)

        self.modified_by = user
        self.modified_at = timezone.now()
        self.save()

        self.finalitemcategory_set.all().delete()
        self._add_category_lists(primary_categories, secondary_categories)

        self.itemtagcategory_set.all().delete()
        self.set_item_tag_categories(tag_category_list)

        post_update_finalitem(self, pre_update_data)

    def categories_defined(self):
        if self.itemtype == 'D' and self.status == 'F':
            return set(Category.objects.filter(finalitemcategory__item=self, finalitemcategory__primary=True))
        return set()

    def categories_referenced(self):
        return set(Category.objects.filter(itemtagcategory__item=self))

    def update_points(self):
        sum_aggregate = ItemValidation.objects.filter(item=self, points__gt=0).aggregate(Sum('points'))
        validation_points = sum_aggregate['points__sum'] or 0
        sum_aggregate = FinalItem.objects.filter(parent=self, status='F', points__gt=0).aggregate(Sum('points'))
        child_points = sum_aggregate['points__sum'] or 0
        points = 1 + validation_points + child_points
        if points != self.points:
            self.points = points
            self.save()
            if self.parent:
                self.parent.update_points()
            post_update_finalitem_points(self)

    def get_name(self):
        items = [self.get_itemtype_display().capitalize(), ' ', self.final_id]
        if self.parent:
            items.extend([' of ', self.parent.get_name()])
        return ''.join(items)

    def get_link(self):
        return reverse('items.views.show_final', args=[self.final_id])


class FinalItemCategory(models.Model):
    class Meta:
        db_table = 'final_item_category'
        unique_together = ('item', 'category')
    item = models.ForeignKey(FinalItem, db_index=True)
    category = models.ForeignKey(Category, db_index=False)
    primary = models.BooleanField()

class ItemTagCategory(models.Model):
    class Meta:
        db_table = 'item_tag_category'
        unique_together = ('item', 'tag')
    item = models.ForeignKey(FinalItem, db_index=True)
    tag = models.ForeignKey(Tag, db_index=False)
    category = models.ForeignKey(Category, db_index=False)
    def __str__(self):
        return '{} | {} | {}'.format(self.item, self.tag, self.category)
    def json_data(self):
        return dict(tag=self.tag, category=self.category)

class ItemValidation(ValidationBase):
    class Meta:
        db_table = 'item_validation'

    item = models.ForeignKey(FinalItem)

    def json_data(self, user=None):
        data = {
            'id':       self.id,
            'source':   self.source.json_data(),
            'location': self.location,
            'points':   self.points
        }
        if user and user.is_authenticated():
            try:
                vote = UserItemValidation.objects.filter(validation=self, created_by=user.id).exclude(value=0).get()
                data.update(user_vote='up' if vote.value > 0 else 'down')
            except UserItemValidation.DoesNotExist:
                pass
        return data

    def update_points(self):
        sum_aggregate = UserItemValidation.objects.filter(validation=self).aggregate(Sum('value'))
        points = sum_aggregate['value__sum'] or 0
        if points != self.points:
            self.points = points
            self.save()
            self.item.update_points()

class UserItemValidation(models.Model):
    class Meta:
        db_table = 'user_item_validation'
        unique_together = ('validation', 'created_by')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', db_index=False)
    created_at = models.DateTimeField(default=timezone.now)
    validation = models.ForeignKey(ItemValidation)
    value = models.IntegerField(default=1, null=False)
