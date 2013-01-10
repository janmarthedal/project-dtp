from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    class Meta:
        db_table = 'tags'
    name   = models.CharField(max_length=255)
    normal = models.CharField(max_length=255, db_index=True)
    def __unicode__(self):
        return self.name


class Item(models.Model):
    class Meta:
        db_table = 'items'

    KIND_CHOICES = (
        ('D', 'definition'),
        ('T', 'theorem'),
        ('P', 'proof'),
        ('I', 'info')
    )

    STATUS_CHOICES = (
        ('D', 'draft'),
        ('R', 'review'),
        ('F', 'final'),
        ('S', 'suspended'),
        ('B', 'broken')
    )

    kind        = models.CharField(max_length=1, choices=KIND_CHOICES)
    status      = models.CharField(max_length=1, choices=STATUS_CHOICES)
    created_by  = models.ForeignKey(User, related_name='+')
    created_at  = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(User, related_name='+')
    modified_at = models.DateTimeField(auto_now=True)
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
        return "%s %i" % (self.get_cap_kind(), self.id)

    def get_absolute_url(self):
        return self.final_id

    #@models.permalink
    #def get_absolute_url(self):
    #    return ('main.views.show_item', [self.alias])

    def __unicode__(self):
        ret = self.get_cap_kind_with_id()
        if self.parent:
            ret += " (%s)" % self.parent.get_cap_kind_with_id()
        return ret

    def clean_fields(self, exclude=None):
        models.Model.clean_fields(self, exclude)
        """
        # check kind
        self.kind = get_string_value(self.kind)
        if self.kind not in [n for (n, _) in self.KIND_CHOICES]:
            raise ValidationError('kind wrong choice')
        # check status
        self.status = get_string_value(self.status)
        if self.status not in [n for (n, _) in self.STATUS_CHOICES]:
            raise ValidationError('status wrong choice')
        """

    def clean(self):
        models.Model.clean(self)
        """
        if self.kind == 'P':
            if self.parent is None:
                raise ValidationError('parent missing')
            if self.parent.kind != 'T':
                raise ValidationError('proof parent must be theorem')
        elif self.kind == 'I':
            if self.parent is None:
                raise ValidationError('parent missing')
            if self.parent.kind == 'I':
                raise ValidationError('info parent cannot be info')
        elif self.parent is not None:
            raise ValidationError('parent should be null')
        """


class ItemTag(models.Model):
    class Meta:
        db_table = 'item_tags'
    item    = models.ForeignKey(Item)
    tag     = models.ForeignKey(Tag)
    primary = models.BooleanField()


