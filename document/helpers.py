from django.shortcuts import get_object_or_404
from django.template import Context
from django.template.loader import get_template
from document.models import DocumentItemEntry
from items.models import FinalItem
from tags.models import Category

import logging
logger = logging.getLogger(__name__)

STEP_SIZE = 100

def render_template(template_name, **kwargs):
    t = get_template(template_name)
    c = Context(dict(**kwargs))
    return t.render(c)

def entry_before(a, b):
    return a.concept_defs.isdisjoint(b.concept_uses) and a.item_defs.isdisjoint(b.item_uses)

class DocumentMessageEntry(object):
    def __init__(self, msgtype, order, **kwargs):
        self.data = dict(type = msgtype, order = order)
        self.data.update(**kwargs)
    def get_categories_used(self):
        return set()
    def json_data(self):
        return self.data

class DocumentView(object):

    def __init__(self, document):
        self.document = document
        self.entries = list(DocumentItemEntry.objects.filter(document=document).all())
        self.items_in_doc = set()
        for entry in self.entries:
            entry.init_meta()
            self.items_in_doc.update(entry.item_defs)
        self.entries.sort(key=lambda entry: entry.order)

    def _order_before_entry_at(self, pos):
        if not self.entries:
            return STEP_SIZE
        elif pos == len(self.entries):
            return self.entries[-1].order + STEP_SIZE
        elif pos == 0:
            return 0.5 * self.entries[0].order
        return 0.5 * (self.entries[pos - 1].order + self.entries[pos].order)

    def _pos_for_key(self, key):
        for k in range(0, len(self.entries)):
            if self.entries[k].key == key:
                return k
        return None

    def insert(self, entry):
        entry.init_meta()
        if self.items_in_doc.isdisjoint(entry.item_uses):
            pos = 0
            while pos < len(self.entries) and entry_before(entry, self.entries[pos]):
                pos += 1
        else:
            pos = len(self.entries)
            while pos > 0 and entry_before(self.entries[pos - 1], entry):
                pos -= 1
        entry.order = self._order_before_entry_at(pos)
        entry.save()
        self.entries.insert(pos, entry)
        self.items_in_doc.update(entry.item_defs)
        return pos

    def add_item(self, item_id):
        item = get_object_or_404(FinalItem, final_id=item_id)
        item_entry = DocumentItemEntry(document=self.document, item=item)
        self.insert(item_entry)
        return [item_entry]

    def add_concept(self, tag_list, source_id):
        category = Category.objects.from_tag_list(tag_list)
        try:
            item = FinalItem.objects.get(itemtype='D', status='F', finalitemcategory__primary=True, finalitemcategory__category=category)
            item_entry = DocumentItemEntry(document=self.document, item=item)
            pos = self.insert(item_entry)
            order = self._order_before_entry_at(pos)
            msg_entry = DocumentMessageEntry('add-concept-success', order, name = unicode(item), concept = category.id)
            return [item_entry, msg_entry]
        except FinalItem.DoesNotExist:
            pos = self._pos_for_key(source_id)
            assert pos is not None
            order = self._order_before_entry_at(pos)
            msg_entry = DocumentMessageEntry('concept-not-found', order, concept = category.id)
            return [msg_entry]

    def delete(self, item_id):
        assert len(item_id) > 5 and item_id[:5] == 'item-'
        item = FinalItem.objects.get(status='F', final_id=item_id[5:])
        pos = self._pos_for_key(item_id)
        assert pos is not None
        # compute order here so we don't end up with the same order as the deleted entry
        order = self._order_before_entry_at(pos)
        item_entry = self.entries.pop(pos)
        assert item_entry.item == item
        self.items_in_doc.difference_update(item_entry.item_defs)
        item_entry.delete()
        msg_entry = DocumentMessageEntry('item-removed', order, entryid = item_entry.key, name = unicode(item))
        return [msg_entry]

    def json_data_for_entries(self, entries):
        category_ids = set()
        for entry in entries:
            category_ids.update(entry.get_categories_used())
        concept_map = []
        for cid in category_ids:
            category = Category.objects.get(pk=cid)
            concept_map.append((category.id, category.json_data()))
        return dict(items = [entry.json_data() for entry in entries],
                    concept_map = concept_map)

    def json_data(self):
        return self.json_data_for_entries(self.entries)
