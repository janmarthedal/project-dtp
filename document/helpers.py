from django.shortcuts import get_object_or_404
from document.models import DocumentItemEntry, DocumentConceptEntry
from items.models import FinalItem
from tags.models import Category

import logging
logger = logging.getLogger(__name__)

class DocumentView(object):

    def __init__(self, document):
        self.document = document
        self.entries = list(DocumentItemEntry.objects.filter(document=document).all())
        self.entries.extend(list(DocumentConceptEntry.objects.filter(document=document).all()))
        for entry in self.entries:
            entry.init_meta()
        self.entries.sort(key=lambda entry: entry.order)

    def add_item(self, item_id):
        item = get_object_or_404(FinalItem, final_id=item_id)
        item_entry = DocumentItemEntry(document=self.document, item=item)
        item_entry.order = self.entries[-1].order + 1 if len(self.entries) else 0
        item_entry.save()
        item_entry.init_meta()
        self.entries.append(item_entry)
        return item_entry

    def add_concept(self, tag_list):
        category = Category.objects.from_tag_list(tag_list)
        item = FinalItem.objects.filter(itemtype='D', status='F', finalitemcategory__primary=True, finalitemcategory__category=category)[0]
        concept_entry = DocumentConceptEntry(document=self.document, category=category, item=item)
        concept_entry.order = self.entries[-1].order + 1 if len(self.entries) else 0
        concept_entry.save()
        concept_entry.init_meta()
        self.entries.append(concept_entry)
        return concept_entry

    def json_data_for_entries(self, entries):
        category_set = set()
        for entry in entries:
            category_set.update(entry.category_set)
        return dict(items = [entry.json_data() for entry in entries],
                    concept_map = [(c.id, c.json_data()) for c in category_set])

    def json_data(self):
        return self.json_data_for_entries(self.entries)
