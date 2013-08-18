from django.conf import settings
from django.db import models
from django.utils import timezone
from tags.models import Category
from tags.helpers import CategoryCollection

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

    itemtype = models.CharField(max_length=1, choices=TYPE_CHOICES)
    parent   = models.ForeignKey('FinalItem', null=True, db_index=False)
    body     = models.TextField(null=True)

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
        type_key = filter(lambda kc: kc[1] == itemtype, DraftItem.TYPE_CHOICES)[0][0]
        item = DraftItem.objects.create(itemtype   = type_key,
                                        status     = 'D',
                                        created_by = user,
                                        body       = body,
                                        parent     = parent)
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

    status      = models.CharField(max_length=1, choices=STATUS_CHOICES, default='D')
    created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', db_index=False)
    modified_at = models.DateTimeField(default=timezone.now)
    categories  = models.ManyToManyField(Category, through='DraftItemCategory')

    def __unicode__(self):
        return "%s %d" % (self.get_itemtype_display().capitalize(), self.id)

    def _get_item_category_set(self):
        return self.draftitemcategory_set.all()

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

class DraftItemCategory(models.Model):

    class Meta:
        db_table = 'draft_item_category'
        unique_together = ('item', 'category')

    item     = models.ForeignKey(DraftItem, db_index=True)
    category = models.ForeignKey(Category, db_index=False)
    primary  = models.BooleanField()
