from django.db import models
from django.shortcuts import get_object_or_404
from tags.helpers import normalize_tag

class TagManager(models.Manager):
    def fetch(self, name):
        normalized = normalize_tag(name)
        tag = self.get_or_create(name=name, defaults={'normalized': normalized})[0]
        return tag

class CategoryManager(models.Manager):

    def __init__(self):
        super().__init__()
        self._root = None

    @property
    def root(self):
        if self._root is None:
            self._root = self.get(tag__name='')
        return self._root

    def from_tag_list(self, tag_list):
        category = self.root
        for tag in tag_list:
            if not isinstance(tag, Tag):
                tag = Tag.objects.fetch(tag)
            category = self.get_or_create(tag=tag, parent=category)[0]
        return category

    def from_tag_names_or_404(self, tags):
        category = self.root
        for tag_name in tags:
            tag = get_object_or_404(Tag, name=tag_name)
            category = get_object_or_404(Category, tag=tag, parent=category)
        return category

    def default_category_for_tag(self, tag):
        return self.from_tag_list(['unspecified'])

class Tag(models.Model):
    name = models.CharField(max_length=255, db_index=True, unique=True)
    normalized = models.CharField(max_length=255, db_index=True, unique=False)

    objects = TagManager()

    class Meta:
        db_table = 'tags'

    def __str__(self):
        return self.name

    def json_data(self):
        return self.name

class Category(models.Model):
    tag = models.ForeignKey(Tag, related_name='+', db_index=False)
    parent = models.ForeignKey('self', null=True, related_name='+', db_index=False)

    objects = CategoryManager()

    class Meta:
        db_table = 'categories'
        unique_together = ('tag', 'parent')

    def get_tag_list(self):
        if self.parent:
            return self.parent.get_tag_list() + [self.tag]
        return []

    def get_tag_str_list(self):
        return map(str, self.get_tag_list())

    def __str__(self):
        return '{}:[{}]'.format(self.pk, ','.join(self.get_tag_str_list()))

    def json_data(self):
        return [t.json_data() for t in self.get_tag_list()]
