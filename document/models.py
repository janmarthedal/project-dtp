from django.conf import settings
from django.db import models
from django.utils import timezone
from items.models import FinalItem, ItemTagCategory
from tags.models import Category

class Document(models.Model):
    class Meta:
        db_table = 'documents'
    created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', db_index=True)
    created_at  = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(default=timezone.now)
    title       = models.CharField(max_length=255, null=True)
    def __unicode__(self):
        return "%d. %s" % (self.id, self.title)

def get_tag_to_category_map(item):
    tag_to_category_map = {}
    for item_tag_category in ItemTagCategory.objects.filter(item=item).all():
        tag = item_tag_category.tag.name
        category = item_tag_category.category.get_tag_list()
        tag_to_category_map[tag] = category
    return tag_to_category_map

class DocumentItem(models.Model):
    class Meta:
        db_table = 'document_item'
        unique_together = (('document', 'item'), ('document', 'order'))
    document = models.ForeignKey(Document, db_index=True)
    order    = models.FloatField(null=False)
    item     = models.ForeignKey(FinalItem, db_index=False)
    def json_serializable(self):
        return dict(type    = 'item',
                    order   = self.order,
                    name    = unicode(self.item),
                    body    = self.item.body,
                    tag_map = get_tag_to_category_map(self.item))

class DocumentConceptItem(models.Model):
    class Meta:
        db_table = 'document_concept_item'
        unique_together = (('document', 'category'), ('document', 'order'))
    document = models.ForeignKey(Document, db_index=True)
    order    = models.FloatField(null=False)
    category = models.ForeignKey(Category, null=False)
    item     = models.ForeignKey(FinalItem, db_index=False, null=True)
    def json_serializable(self):
        result = dict(type    = 'concept',
                      concept = [t.name for t in self.category.get_tag_list()],
                      order   = self.order)
        if self.item:
            result.update(name    = unicode(self.item),
                          body    = self.item.body,
                          tag_map = get_tag_to_category_map(self.item))
        return result
