import string
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models, IntegrityError
from django.db.models import Sum
from django.utils import timezone
from django.utils.crypto import get_random_string
from tags.models import Category, Tag
from drafts.models import BaseItem
from sources.models import ValidationBase

import logging
logger = logging.getLogger(__name__)

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
        self.modified_by = user
        self.modified_at = timezone.now()
        self.save()

        self.finalitemcategory_set.all().delete()
        self._add_category_lists(primary_categories, secondary_categories)

        self.itemtagcategory_set.all().delete()
        self.set_item_tag_categories(tag_category_list)

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

    def get_name(self):
        items = [self.get_itemtype_display().capitalize(), ' ', self.final_id]
        if self.parent:
            items.extend(' of ', self.parent.get_name())
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
