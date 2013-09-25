from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from items.helpers import BodyScanner
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
    def json_data(self):
        return dict(id=self.id, title=self.title)

class DocumentEntryBase(models.Model):
    class Meta:
        abstract = True
    document = models.ForeignKey(Document, db_index=True)
    order    = models.FloatField(null=False)
    def init_meta(self):
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
        # key
        self.key = 'item-' + self.item.final_id
        # item defs
        self.item_defs.add(self.item.final_id)
        # item uses
        bs = BodyScanner(self.item.body)
        self.item_uses.update(bs.getItemRefSet())
        if self.item.parent:
            self.item_uses.add(self.item.parent.final_id)
        # concept defs
        if self.item.itemtype == 'D':
            self.concept_defs.update(Category.objects.filter(finalitemcategory__item=self.item, finalitemcategory__primary=True).values_list('id', flat=True))
        # tag to concept map / concept defs
        self.tag_refs = {}
        for p in ItemTagCategory.objects.filter(item=self.item).values('tag__name', 'category_id'):
            self.concept_uses.add(p['category_id'])
            self.tag_refs[p['tag__name']] = p['category_id']
    def get_categories_used(self):
        return self.concept_defs | self.concept_uses
    def json_data(self):
        result = self.make_json('item',
                                id           = self.key,
                                name         = unicode(self.item),
                                body         = self.item.body,
                                item_defs    = list(self.item_defs),
                                item_uses    = list(self.item_uses),
                                concept_defs = list(self.concept_defs),
                                tag_refs     = self.tag_refs,  # implicitly concept uses
                                link         = reverse('items.views.show_final', args=[self.item.final_id]))
        return result
