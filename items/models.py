from django.db import models
from django.conf import settings
from django.utils import timezone
from items.helpers import make_short_name
import datetime

import logging
logger = logging.getLogger(__name__)

class Tag(models.Model):
    class Meta:
        db_table = 'tags'
    name = models.CharField(max_length=255, db_index=True)
    def __unicode__(self):
        return self.name

def add_item_tags(item, tags, primary):
    for tag_name in tags:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        itemtag = ItemTag(item=item, tag=tag, primary=primary)
        itemtag.save()

class ItemManager(models.Manager):

    def add_item(self, user, kind, body, primarytags, othertags, parent):
        kind_key = filter(lambda kc: kc[1] == kind, Item.KIND_CHOICES)[0][0]

        item = Item(kind        = kind_key,
                    status      = 'D',
                    created_by  = user,
                    modified_by = user,
                    body        = body,
                    parent      = parent)
        item.save()

        add_item_tags(item, primarytags, True)
        add_item_tags(item, othertags, False)

        return item

    def update_item(self, item, user, body, primarytags, othertags):
        item.modified_by = user
        item.modified_at = timezone.now()
        item.body        = body
        item.save()

        ItemTag.objects.filter(item=item).delete()
        add_item_tags(item, primarytags, True)
        add_item_tags(item, othertags, False)


class Item(models.Model):
    class Meta:
        db_table = 'items'

    objects = ItemManager()

    KIND_CHOICES = (
        ('D', 'definition'),
        ('T', 'theorem'),
        ('P', 'proof'),
        ('I', 'info')
    )

    STATUS_CHOICES = (
        ('D', 'draft'),
        ('R', 'under review'),
        ('F', 'published'),
        ('S', 'suspended'),
        ('B', 'broken')
    )

    kind        = models.CharField(max_length=1, choices=KIND_CHOICES)
    status      = models.CharField(max_length=1, choices=STATUS_CHOICES, default='D')
    created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    created_at  = models.DateTimeField(default=timezone.now)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    modified_at = models.DateTimeField(default=timezone.now)
    final_at    = models.DateTimeField(null=True, blank=True)
    final_id    = models.CharField(max_length=10, db_index=True, unique=True,
                                   null=True, blank=True)
    parent      = models.ForeignKey('self', null=True, blank=True)
    body        = models.TextField(null=True, blank=True)
    tags        = models.ManyToManyField(Tag, blank=True, through='ItemTag', related_name='item_tags')

    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)
        self._cache = {}

    def _set_tag_cache(self):
        tags = [(itemtag.tag.name, itemtag.primary)
                for itemtag in self.itemtag_set.all()]
        self._cache['primary_tags'] = [t[0] for t in tags if t[1]]
        self._cache['other_tags']   = [t[0] for t in tags if not t[1]]

    @property
    def primary_tags(self):
        if 'primary_tags' not in self._cache:
            self._set_tag_cache()
        return self._cache['primary_tags']

    @property
    def other_tags(self):
        if 'other_tags' not in self._cache:
            self._set_tag_cache()
        return self._cache['other_tags']

    def get_cap_kind(self):
        return self.get_kind_display().capitalize()

    def get_cap_kind_with_id(self):
        if self.final_id:
            return "%s %s" % (self.get_cap_kind(), self.final_id)
        if self.id:
            return "%s %i" % (self.get_cap_kind(), self.id)
        return "%s ?" % self.get_cap_kind()

    def __unicode__(self):
        ret = self.get_cap_kind_with_id()
        if self.parent:
            ret += " (%s)" % self.parent.get_cap_kind_with_id()
        return ret

    def make_final(self, user):
        if self.status != 'F':
            self.status      = 'F'
            self.modified_by = user
            self.modified_at = timezone.now()
            self.final_at    = self.modified_at
            for length in range(4, 10+1):
                self.final_id = make_short_name(length)
                try:
                    self.save()
                    break
                except IntegrityError:
                    pass
            logger.debug("Publish of %i successful with final_id '%s'" % (self.id, self.final_id))

    def make_review(self, user):
        if self.status != 'R':
            self.status      = 'R'
            self.modified_by = user
            self.modified_at = timezone.now()
            self.save()
            logger.debug("%i to review successful" % self.id)

class ItemTag(models.Model):
    class Meta:
        db_table = 'item_tags'
    item    = models.ForeignKey(Item)
    tag     = models.ForeignKey(Tag)
    primary = models.BooleanField()


