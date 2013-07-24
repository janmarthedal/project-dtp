from django.db import models
from main.helpers import ListWrapper
from tags.helpers import normalize_tag


class TagManager(models.Manager):

    def fetch(self, name):
        normalized = normalize_tag(name)
        tag = self.get_or_create(name=name, defaults={'normalized':normalized})[0]
        return tag


class Tag(models.Model):

    class Meta:
        db_table = 'tags'
    
    objects    = TagManager()
    name       = models.CharField(max_length=255, db_index=True, unique=True)
    normalized = models.CharField(max_length=255, db_index=True, unique=False)

    def __unicode__(self):
        return self.name
    
    def json_serializable(self):
        return self.name


class CategoryManager(models.Manager):

    def from_tag_list(self, tag_list):
        category = None
        for tag_name in tag_list:
            tag = Tag.objects.fetch(tag_name)
            category = self.get_or_create(tag=tag, parent=category)[0]
        return category


class Category(models.Model):

    class Meta:
        db_table = 'categories'
        unique_together = ('tag', 'parent')

    objects = CategoryManager()

    tag    = models.ForeignKey(Tag, related_name='+', db_index=False)
    parent = models.ForeignKey('self', null=True, related_name='+', db_index=False)

    def get_tag_list(self):
        tag_list = self.parent.get_tag_list()[:] if self.parent else []
        tag_list.append(self.tag)
        return tag_list

    def __unicode__(self):
        return u'%d:[%s]' % (self.pk, u','.join([unicode(tag) for tag in self.get_tag_list()]))

    def json_serializable(self):
        return self.get_tag_list()
