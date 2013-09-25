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

class DocumentItemEntry(models.Model):
    class Meta:
        db_table = 'document_item_entry'
        unique_together = (('document', 'item'), ('document', 'order'))
    document = models.ForeignKey(Document, db_index=True)
    order    = models.FloatField(null=False)
    item     = models.ForeignKey(FinalItem, db_index=False)
    def init_meta(self):
        self.extra = {}
        # key
        self.key = 'item-' + self.item.final_id
        # item defs
        self.item_defs = set([self.item.final_id])
        # item uses
        bs = BodyScanner(self.item.body)
        self.item_uses = set(bs.getItemRefSet())
        if self.item.parent:
            self.item_uses.add(self.item.parent.final_id)
        # concept defs
        self.concept_defs = set()
        if self.item.itemtype == 'D':
            self.concept_defs.update(Category.objects.filter(finalitemcategory__item=self.item, finalitemcategory__primary=True).values_list('id', flat=True))
        # tag to concept map / concept uses
        self.concept_uses = set()
        self.tag_refs = {}
        for p in ItemTagCategory.objects.filter(item=self.item).values('tag__name', 'category_id'):
            self.concept_uses.add(p['category_id'])
            self.tag_refs[p['tag__name']] = p['category_id']
    def get_categories_used(self):
        return self.concept_defs | self.concept_uses
    def json_data(self):
        result = dict(type         = 'item',
                      order        = self.order,
                      id           = self.key,
                      name         = unicode(self.item),
                      body         = self.item.body,
                      item_defs    = list(self.item_defs),
                      item_uses    = list(self.item_uses),
                      concept_defs = list(self.concept_defs),
                      tag_refs     = self.tag_refs,  # implicitly concept uses
                      link         = reverse('items.views.show_final', args=[self.item.final_id]))
        result.update(self.extra)
        return result
