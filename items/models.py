import random
from django.db import models, IntegrityError
from django.conf import settings
from django.utils import timezone
from tags.models import Tag
from items.helpers import BodyScanner

import logging
logger = logging.getLogger(__name__)


FINAL_NAME_CHARS = '23456789abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
FINAL_NAME_MIN_LENGTH = 4

def final_id_to_name(value):
    base = len(FINAL_NAME_CHARS)
    length = FINAL_NAME_MIN_LENGTH
    while value >= base**length:
        value -= base**length
        length += 1
    name = ''
    while length > 0:
        name = FINAL_NAME_CHARS[value % base] + name
        value /= base
        length -= 1
    return name

def final_name_to_id(name):
    if len(name) < FINAL_NAME_MIN_LENGTH:
        raise ValueError('Public id too short')
    base = len(FINAL_NAME_CHARS)
    value = 0
    for c in name:
        idx = FINAL_NAME_CHARS.find(c)
        if idx < 0:
            raise ValueError('Illegal character in public id')
        value = base*value + idx
    length = FINAL_NAME_MIN_LENGTH
    while length < len(name):
        value += base**length
        length += 1
    return value



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
        base = len(FINAL_NAME_CHARS)
        max_val = base**FINAL_NAME_MIN_LENGTH
        while True:
            item.id = random.randint(0, max_val - 1)
            try:
                item.save()
                break
            except IntegrityError:
                max_val *= 64

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

    id           = models.BigIntegerField(primary_key=True)
    status       = models.CharField(max_length=1, choices=STATUS_CHOICES, default='F')
    created_by   = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    created_at   = models.DateTimeField(default=timezone.now)
    modified_by  = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+')
    modified_at  = models.DateTimeField(default=timezone.now)
    tags         = models.ManyToManyField(Tag, through='FinalItemTag')

    def public_id(self):
        return final_id_to_name(self.id)

    def __unicode__(self):
        return "%s %s" % (self.get_itemtype_display().capitalize(), self.public_id())

    def _set_tag_cache(self):
        tags = [(itemtag.tag.name, itemtag.primary)
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
        tags = [(itemtag.tag.name, itemtag.primary)
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
    item    = models.ForeignKey(DraftItem)
    tag     = models.ForeignKey(Tag)
    primary = models.BooleanField()


class FinalItemTag(models.Model):
    class Meta:
        db_table = 'final_item_tags'
    item    = models.ForeignKey(FinalItem)
    tag     = models.ForeignKey(Tag)
    primary = models.BooleanField()

