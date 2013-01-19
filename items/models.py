from django.db import models
from django.contrib.auth.models import User
from items.helpers import make_short_name
import datetime

class Tag(models.Model):
    class Meta:
        db_table = 'tags'
    name = models.CharField(max_length=255, db_index=True)
    def __unicode__(self):
        return self.name

class ItemManager(models.Manager):
    def add_item(self, user, kind, body, tags):
        kind_key = filter(lambda kc: kc[1] == kind, Item.KIND_CHOICES)[0][0]

        item = Item(kind        = kind_key,
                    status      = 'D',
                    created_by  = user,
                    created_at  = datetime.datetime.utcnow(),
                    modified_by = user,
                    modified_at = datetime.datetime.utcnow(),
                    body        = body)
        item.save()
        
        for tag_name, is_primary in tags.iteritems():
            tag, created = Tag.objects.get_or_create(name=tag_name)
            itemtag = ItemTag(item=item, tag=tag, primary=is_primary)
            itemtag.save()

        return item.id

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
    created_by  = models.ForeignKey(User, related_name='+')
    created_at  = models.DateTimeField()
    modified_by = models.ForeignKey(User, related_name='+')
    modified_at = models.DateTimeField()
    final_at    = models.DateTimeField(null=True, blank=True)
    final_id    = models.CharField(max_length=10, db_index=True, unique=True,
                                   null=True, blank=True)
    parent      = models.ForeignKey('self', null=True, blank=True)
    body        = models.TextField(null=True, blank=True)
    tags        = models.ManyToManyField(Tag, blank=True, through='ItemTag')
    deps        = models.ManyToManyField('self', blank=True)

    def get_cap_kind(self):
        return self.get_kind_display().capitalize()

    def get_cap_kind_with_id(self):
	if self.final_id:
            return "%s %s" % (self.get_cap_kind(), self.final_id)
        if self.id:
            return "%s %i" % (self.get_cap_kind(), self.id)
        return "%s ?" % self.get_cap_kind()

    def get_absolute_url(self):
        return self.final_id

    def __unicode__(self):
        ret = self.get_cap_kind_with_id()
        if self.parent:
            ret += " (%s)" % self.parent.get_cap_kind_with_id()
        return ret

    def make_final(self, user):
        if not self.final_id:
            self.status = 'F'
            self.modified_by = user
            self.final_id = make_short_name(4)
            self.final_at = datetime.datetime.utcnow()
            self.save()
        return self.final_id

class ItemTag(models.Model):
    class Meta:
        db_table = 'item_tags'
    item    = models.ForeignKey(Item)
    tag     = models.ForeignKey(Tag)
    primary = models.BooleanField()


