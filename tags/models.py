from django.db import models
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

class CategoryManager(models.Manager):
    def fetch(self, tag_list):
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
    tag     = models.ForeignKey(Tag, related_name='+')
    parent  = models.ForeignKey('self', null=True, related_name='+')
    
    def get_tag_list(self):
        tag_list = []
        category = self
        while category:
            tag_list.append(category.tag)
            category = category.parent
        tag_list.reverse()
        return tag_list
    
    def get_tag_names(self):
        return [tag.name for tag in self.get_tag_list()]
    
    def __unicode__(self):
        return unicode(self.get_tag_names())
                             