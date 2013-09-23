from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from items.helpers import BodyScanner
from items.models import FinalItem, ItemTagCategory

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
    def init_meta(self):
        self.category_set = set()   # Category models
        self.concept_defs = set()   # Category ids (ints)
        self.concept_uses = set()   # Category ids (ints)
        self.item_defs = set()      # FinalItem ids (strings)
        self.item_uses = set()      # FinalItem ids (strings)
        self.key = None
    def make_json(self, entry_type, **kwargs):
        result = dict(type = entry_type, order = self.order)
        result.update(**kwargs)
        return result

class DocumentItemEntry(DocumentEntryBase):
    class Meta:
        db_table = 'document_item_entry'
        unique_together = (('document', 'item'), ('document', 'order'))
    item = models.ForeignKey(FinalItem, db_index=False)
    def init_meta(self):
        super(DocumentItemEntry, self).init_meta()
        self.key = 'item-' + self.item.final_id
        bs = BodyScanner(self.item.body)
        if self.item.itemtype == 'D':
            self.category_set.update(self.item.primary_categories)
            self.concept_defs.update([c.id for c in self.item.primary_categories])
        self.item_defs.add(self.item.final_id)
        self.item_uses.update(bs.getItemRefSet())
        self.tag_refs = {}
        for item_tag_category in ItemTagCategory.objects.filter(item=self.item).all():
            self.category_set.add(item_tag_category.category)
            self.concept_uses.add(item_tag_category.category.id)
            self.tag_refs[item_tag_category.tag.name] = item_tag_category.category.id
    def json_data(self):
        result = self.make_json('item',
                                id           = self.key,
                                name         = unicode(self.item),
                                body         = self.item.body,
                                tag_refs     = self.tag_refs,
                                concept_defs = list(self.concept_defs),
                                item_uses    = list(self.item_uses),
                                link         = reverse('items.views.show_final', args=[self.item.final_id]))
        return result
