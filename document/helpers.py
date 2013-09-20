from django.shortcuts import get_object_or_404
from django.template import Context
from django.template.loader import get_template
from document.models import DocumentItemEntry
from items.models import FinalItem
from tags.models import Category

import logging
logger = logging.getLogger(__name__)

STEP_SIZE = 100

class DocumentMessageEntry(object):
    def __init__(self, severity, msg, source_id):
        self.severity = severity
        self.msg = msg
        self.source_id = source_id
        self.category_set = set()
    def json_data(self):
        return dict(type = 'message', severity = self.severity, message = self.msg,
                    source_id = self.source_id, order = 0)

class DocumentView(object):

    def __init__(self, document):
        self.document = document
        self.entries = list(DocumentItemEntry.objects.filter(document=document).all())
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
                pos += 1
            if pos == len(self.entries):
                entry.order = self.entries[-1].order + STEP_SIZE
            elif pos == 0:
                entry.order = 0.5 * self.entries[0].order
            else:
                entry.order = 0.5 * (self.entries[pos - 1].order + self.entries[pos].order)
        else:
            entry.order = STEP_SIZE
        entry.save()
        self.entries.insert(pos, entry)
        return entry

    def add_item(self, item_id):
        item = get_object_or_404(FinalItem, final_id=item_id)
        item_entry = DocumentItemEntry(document=self.document, item=item)
        return self.insert(item_entry)

    def add_concept(self, tag_list, source_id):
        category = Category.objects.from_tag_list(tag_list)
        try:
            item = FinalItem.objects.filter(itemtype='D', status='F', finalitemcategory__primary=True, finalitemcategory__category=category)[0]
            concept_entry = DocumentItemEntry(document=self.document, item=item)
            return self.insert(concept_entry)
        except IndexError:
            t = get_template('document/no_defs_found.html')
            c = Context(dict(category=category))
            return DocumentMessageEntry('warning', t.render(c), source_id)

    def json_data_for_entries(self, entries):
        category_set = set()
        for entry in entries:
            category_set.update(entry.category_set)
        return dict(items       = [entry.json_data() for entry in entries],
                    concept_map = [(c.id, c.json_data()) for c in category_set])

    def json_data(self):
        return self.json_data_for_entries(self.entries)
