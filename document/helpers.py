from django.shortcuts import get_object_or_404
from document.models import DocumentItemEntry, DocumentConceptEntry
from items.models import FinalItem
from tags.models import Category

import logging
logger = logging.getLogger(__name__)

STEP_SIZE = 100

class DocumentView(object):

    def __init__(self, document):
        self.document = document
        self.entries = list(DocumentItemEntry.objects.filter(document=document).all())
        self.entries.extend(list(DocumentConceptEntry.objects.filter(document=document).all()))
        for entry in self.entries:
            entry.init_meta()
        self.entries.sort(key=lambda entry: entry.order)

    def insert(self, entry):
        entry.init_meta()
        pos = 0
        if len(self.entries):
            while (pos < len(self.entries)
                   and entry.concept_defs.isdisjoint(self.entries[pos].concept_uses)
                   and entry.item_defs.isdisjoint(self.entries[pos].item_uses)):
                pos += STEP_SIZE
            if pos == len(self.entries):
                entry.order = self.entries[-1].order + STEP_SIZE
            elif pos == 0:
                entry.order = 0.5 * self.entries[0].order
            else:
                entry.order = 0.5 * (self.entries[pos - 1].order + self.entries[pos].order)
        else:
            entry.order = STEP_SIZE
        logger.debug('pos %d, order %f' % (pos, entry.order))
        entry.save()
        self.entries.insert(pos, entry)

    def add_item(self, item_id):
        item = get_object_or_404(FinalItem, final_id=item_id)
        item_entry = DocumentItemEntry(document=self.document, item=item)
        self.insert(item_entry)
        return item_entry

    def add_concept(self, tag_list):
        category = Category.objects.from_tag_list(tag_list)
        item = FinalItem.objects.filter(itemtype='D', status='F', finalitemcategory__primary=True, finalitemcategory__category=category)[0]
        concept_entry = DocumentConceptEntry(document=self.document, category=category, item=item)
        self.insert(concept_entry)
        return concept_entry

    def json_data_for_entries(self, entries):
        category_set = set()
        for entry in entries:
            category_set.update(entry.category_set)
        return dict(items       = [entry.json_data() for entry in entries],
                    concept_map = [(c.id, c.json_data()) for c in category_set])

    def json_data(self):
        return self.json_data_for_entries(self.entries)
