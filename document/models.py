from django.conf import settings
from django.db import models
from django.utils import timezone
from items.helpers import BodyScanner
from items.models import FinalItem, ItemTagCategory
from tags.helpers import CategoryCollection
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

class DocumentEntryBase(models.Model):
    class Meta:
        abstract = True
    document = models.ForeignKey(Document, db_index=True)
    order    = models.FloatField(null=False)
    def make_json(self, entry_type, **kwargs):
        result = dict(type = entry_type, order = self.order)
        result.update(**kwargs)
        return result

class DocumentItemEntryBase(DocumentEntryBase):
    class Meta:
        abstract = True
    item = models.ForeignKey(FinalItem, db_index=False)
    def init_meta(self):
        bs = BodyScanner(self.item.body)
        self.category_set = set()
        if self.item.itemtype == 'D':
            self.category_set.update(self.item.primary_categories)
            self.concept_defs = [c.id for c in self.item.primary_categories]
        else:
            self.concept_defs = []
        self.item_uses = bs.getItemRefSet()
        self.tag_refs = {}
        for item_tag_category in ItemTagCategory.objects.filter(item=self.item).all():
            self.category_set.add(item_tag_category.category)
            self.tag_refs[item_tag_category.tag.name] = item_tag_category.category.id
    def make_json(self, entry_type, **kwargs):
        result = super(DocumentItemEntryBase, self).make_json(entry_type, **kwargs)
        result.update(name         = unicode(self.item),
                      body         = self.item.body,
                      tag_refs     = self.tag_refs,
                      concept_defs = self.concept_defs,
                      item_uses    = self.item_uses)
        return result

class DocumentItemEntry(DocumentItemEntryBase):
    class Meta:
        db_table = 'document_item_entry'
        unique_together = (('document', 'item'), ('document', 'order'))
    def json_data(self):
        return self.make_json('item')

class DocumentConceptEntry(DocumentItemEntryBase):
    class Meta:
        db_table = 'document_concept_entry'
        unique_together = (('document', 'category'), ('document', 'order'))
    category = models.ForeignKey(Category, null=False)
    def init_meta(self):
        super(DocumentConceptEntry, self).init_meta()
        self.category_set.add(self.category)
    def json_data(self):
        return self.make_json('concept', concept = self.category.id)
