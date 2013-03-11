from django.db import models, IntegrityError
from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string
from tags.models import Tag

import logging
logger = logging.getLogger(__name__)


FINAL_NAME_CHARS = '23456789abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
FINAL_NAME_MIN_LENGTH = 4

class BaseItem(models.Model):

    class Meta:
        abstract = True

    TYPE_CHOICES = (
        ('D', 'definition'),
        ('T', 'theorem'),
        ('P', 'proof'),
        ('I', 'info')
    )

    def __init__(self, *args, **kwargs):
        super(BaseItem, self).__init__(*args, **kwargs)
        self._cache = {}

    @property
    def primary_tags(self):
        if 'primary_tags' not in self._cache:
            self._set_tag_cache()
        return self._cache['primary_tags']

    @property
    def secondary_tags(self):
        if 'secondary_tags' not in self._cache:
            self._set_tag_cache()
        return self._cache['secondary_tags']

    itemtype = models.CharField(max_length=1, choices=TYPE_CHOICES)
    parent   = models.ForeignKey('FinalItem', null=True)
    body     = models.TextField(null=True)


class FinalItemManager(models.Manager):

    def add_item(self, draft_item):
        item = FinalItem(itemtype    = draft_item.itemtype,
                         status      = 'F',
                         created_by  = draft_item.created_by,
                         modified_by = draft_item.created_by,
                         body        = draft_item.body,
                         parent      = draft_item.parent)
        length = FINAL_NAME_MIN_LENGTH
        while True:
            item.final_id = get_random_string(length, FINAL_NAME_CHARS)
            try:
                item.save()
                break
            except IntegrityError:
                length += 1

        for draftitemtag in draft_item.draftitemtag_set.all():
            finalitemtag = FinalItemTag(item=item, tag=draftitemtag.tag,
                                        primary=draftitemtag.primary)
            finalitemtag.save()

        return item


class FinalItem(BaseItem):

    class Meta:
        db_table = 'final_items'

    objects = FinalItemManager()

    STATUS_CHOICES = (
        ('F', 'published'),
        ('S', 'suspended'),
        ('B', 'broken')
    )

    final_id     = models.CharField(max_length=10, unique=True, db_index=True)
    status       = models.CharField(max_length=1, choices=STATUS_CHOICES, default='F')
    created_by   = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    created_at   = models.DateTimeField(default=timezone.now)
    modified_by  = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    modified_at  = models.DateTimeField(default=timezone.now)
    tags         = models.ManyToManyField(Tag, through='FinalItemTag')

    def __unicode__(self):
        return "%s %s" % (self.get_itemtype_display().capitalize(), self.final_id)

    def _set_tag_cache(self):
        tags = [(itemtag.tag, itemtag.primary)
                for itemtag in self.finalitemtag_set.all()]
        self._cache['primary_tags']   = [t[0] for t in tags if t[1]]
        self._cache['secondary_tags'] = [t[0] for t in tags if not t[1]]


class DraftItemManager(models.Manager):

    def _add_tags(self, item, primary_tags, secondary_tags):
        for name in primary_tags:
            DraftItemTag(item=item, tag=Tag.objects.fetch(name), primary=True).save()
        for name in secondary_tags:
            DraftItemTag(item=item, tag=Tag.objects.fetch(name), primary=False).save()

    def add_item(self, user, itemtype, body, primary_tags, secondary_tags, parent):
        type_key = filter(lambda kc: kc[1] == itemtype, DraftItem.TYPE_CHOICES)[0][0]

        item = DraftItem(itemtype   = type_key,
                         status     = 'D',
                         created_by = user,
                         body       = body,
                         parent     = parent)
        item.save()

        self._add_tags(item, primary_tags, secondary_tags)

        return item

    def update_item(self, item, user, body, primary_tags, secondary_tags):
        item.modified_at = timezone.now()
        item.body        = body
        item.save()

        item.draftitemtag_set.all().delete()
        self._add_tags(item, primary_tags, secondary_tags)


class DraftItem(BaseItem):

    class Meta:
        db_table = 'draft_items'

    objects = DraftItemManager()

    STATUS_CHOICES = (
        ('D', 'draft'),
        ('R', 'under review'),
    )

    status      = models.CharField(max_length=1, choices=STATUS_CHOICES, default='D')
    created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    modified_at = models.DateTimeField(default=timezone.now)
    tags        = models.ManyToManyField(Tag, through='DraftItemTag')

    def __unicode__(self):
        return "%s %d" % (self.get_itemtype_display().capitalize(), self.id)

    def _set_tag_cache(self):
        tags = [(itemtag.tag, itemtag.primary)
                for itemtag in self.draftitemtag_set.all()]
        self._cache['primary_tags']   = [t[0] for t in tags if t[1]]
        self._cache['secondary_tags'] = [t[0] for t in tags if not t[1]]

    def make_review(self):
        if self.status != 'R':
            self.status      = 'R'
            self.modified_at = timezone.now()
            self.save()
            logger.debug("%d to review successful" % self.id)


class DraftItemTag(models.Model):
    class Meta:
        db_table = 'draft_item_tags'
        unique_together = ('item', 'tag')
    item    = models.ForeignKey(DraftItem)
    tag     = models.ForeignKey(Tag)
    primary = models.BooleanField()


class FinalItemTag(models.Model):
    class Meta:
        db_table = 'final_item_tags'
        unique_together = ('item', 'tag')
    item    = models.ForeignKey(FinalItem)
    tag     = models.ForeignKey(Tag)
    primary = models.BooleanField()

