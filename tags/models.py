from django.db import models
from django.shortcuts import get_object_or_404
from tags.helpers import normalize_tag

class TagManager(models.Manager):
    def fetch(self, name):
        normalized = normalize_tag(name)
        tag = self.get_or_create(name=name, defaults={'normalized': normalized})[0]
        return tag

class Tag(models.Model):
    class Meta:
        db_table = 'tags'

    objects = TagManager()
    name = models.CharField(max_length=255, db_index=True, unique=True)
    normalized = models.CharField(max_length=255, db_index=True, unique=False)

    def __str__(self):
        return self.name

    def json_data(self):
        return self.name

class CategoryManager(models.Manager):
    def from_tag_list(self, tag_list):
        category = None
        for tag in tag_list:
            if not isinstance(tag, Tag):
                tag = Tag.objects.fetch(tag)
            category = self.get_or_create(tag=tag, parent=category)[0]
        return category

    def from_tag_names_or_404(self, tags):
        category = None
        for tag_name in tags:
            tag = get_object_or_404(Tag, name=tag_name)
            category = get_object_or_404(Category, tag=tag, parent=category)
        return category

    def default_category_for_tag(self, tag):
        return self.from_tag_list(['unspecified'])

class Category(models.Model):
    class Meta:
        db_table = 'categories'
        unique_together = ('tag', 'parent')

    objects = CategoryManager()
    tag = models.ForeignKey(Tag, related_name='+', db_index=False)
    parent = models.ForeignKey('self', null=True, related_name='+', db_index=False)

    def get_tag_list(self):
        if self.parent:
            return self.parent.get_tag_list() + [self.tag]
        return [self.tag]

    def __str__(self):
        return '{}:[{}]'.format(self.pk, ','.join(map(str, self.get_tag_list())))

    def json_data(self):
        return [t.json_data() for t in self.get_tag_list()]
