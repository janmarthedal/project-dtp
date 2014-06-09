from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from tags.models import Category
from tags.helpers import CategoryCollection
from sources.models import ValidationBase

import logging
logger = logging.getLogger(__name__)

class BaseItem(models.Model):
    class Meta:
        abstract = True

    TYPE_CHOICES = (
        ('D', 'definition'),
        ('T', 'theorem'),
        ('P', 'proof'),
        ('I', 'info')
    )

    @staticmethod
    def type_name_to_type_key(type_name):
        return [kc[0] for kc in BaseItem.TYPE_CHOICES if kc[1] == type_name][0]

    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(default=timezone.now)
    itemtype = models.CharField(max_length=1, choices=TYPE_CHOICES)
    parent = models.ForeignKey('items.FinalItem', null=True, db_index=False)
    body = models.TextField(null=True)

    def __init__(self, *args, **kwargs):
        super(BaseItem, self).__init__(*args, **kwargs)
        self._cache = {}

    def _add_category_lists(self, primary_categories, secondary_categories):
        self._add_category_list(primary_categories, True)
        self._add_category_list(secondary_categories, False)

    def _set_category_cache(self):
        categories = [(itemcat.category, itemcat.primary)
                      for itemcat in self._get_item_category_set()]
        self._cache['primary_categories']   = CategoryCollection([t[0] for t in categories if t[1]])
        self._cache['secondary_categories'] = CategoryCollection([t[0] for t in categories if not t[1]])

    @property
    def primary_categories(self):
        if 'primary_categories' not in self._cache:
            self._set_category_cache()
        return self._cache['primary_categories']

    @property
    def secondary_categories(self):
        if 'secondary_categories' not in self._cache:
            self._set_category_cache()
        return self._cache['secondary_categories']

class DraftItemManager(models.Manager):
    def add_item(self, user, itemtype, body, primary_categories, secondary_categories, parent):
        type_key = BaseItem.type_name_to_type_key(itemtype)
        item = self.create(itemtype=type_key, status='D', created_by=user, body=body, parent=parent)
        item._add_category_lists(primary_categories, secondary_categories)
        return item

class DraftItem(BaseItem):
    class Meta:
        db_table = 'draft_items'

    objects = DraftItemManager()

    STATUS_CHOICES = (
        ('D', 'draft'),
        ('R', 'under review'),
    )

    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='D')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', db_index=False)
    categories = models.ManyToManyField(Category, through='DraftItemCategory')

    def __str__(self):
        return "%s %d" % (self.get_itemtype_display().capitalize(), self.id)

    def _get_item_category_set(self):
        return self.draftitemcategory_set.all()

    def make_draft(self):
        if self.status != 'D':
            self.status = 'D'
            self.modified_at = timezone.now()
            self.save()
            logger.debug("%d to draft successful" % self.id)

    def make_review(self):
        if self.status != 'R':
            self.status = 'R'
            self.modified_at = timezone.now()
            self.save()
            logger.debug("%d to review successful" % self.id)

    def _add_category_list(self, categories, is_primary):
        for tag_list in categories:
            category = Category.objects.from_tag_list(tag_list)
            DraftItemCategory.objects.create(item=self, category=category, primary=is_primary)

    def update(self, body, primary_categories, secondary_categories):
        self.modified_at = timezone.now()
        self.body = body
        self.save()
        self.draftitemcategory_set.all().delete()
        self._add_category_lists(primary_categories, secondary_categories)

    def get_name(self):
        items = [self.get_itemtype_display().capitalize(), ' ', str(self.pk)]
        if self.parent:
            items.extend([' of ', self.parent.get_name()])
        return ''.join(items)

    def get_link(self):
        return reverse('drafts.views.show', args=[self.pk])

class DraftItemCategory(models.Model):
    class Meta:
        db_table = 'draft_item_category'
        unique_together = ('item', 'category')
    item = models.ForeignKey(DraftItem, db_index=True)
    category = models.ForeignKey(Category, db_index=False)
    primary = models.BooleanField()

class DraftValidation(ValidationBase):
    class Meta:
        db_table = 'draft_validation'
    item = models.ForeignKey(DraftItem)

class ReviewEntry(models.Model):
    class Meta:
        db_table = 'review_entry'
    item = models.ForeignKey(DraftItem)
    item_modified_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', db_index=False)
    created_at = models.DateTimeField(default=timezone.now)
    comment = models.TextField()
    weight = models.FloatField()
    points = models.FloatField()

class ReviewEntryVote(models.Model):
    class Meta:
        db_table = 'review_entry_vote'
    review_comment = models.ForeignKey(ReviewEntry)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', db_index=False)
    created_at = models.DateTimeField(default=timezone.now)
    value = models.IntegerField(default=1, null=False)
