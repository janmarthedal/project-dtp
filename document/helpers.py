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

class DocumentMessageEntry(object):
    def __init__(self, severity, msg, order, action=None):
        self.severity = severity
        self.msg = msg
        self.order = order
        self.category_set = set()
        self.action = action
    def json_data(self):
        result = dict(type = 'message', severity = self.severity, message = self.msg, order = self.order)
        if self.action:
            result.update(action = self.action)
        return result

class DocumentView(object):

    def __init__(self, document):
        self.document = document
        self.entries = list(DocumentItemEntry.objects.filter(document=document).all())
        for entry in self.entries:
            entry.init_meta()
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
        if entry.item_uses:
            pos = len(self.entries)
            while (pos > 0 and
                   self.entries[pos - 1].concept_defs.isdisjoint(entry.concept_uses) and
                   self.entries[pos - 1].item_defs.isdisjoint(entry.item_uses)):
                pos -= 1
        else:
            pos = 0
            while (pos < len(self.entries) and
                   entry.concept_defs.isdisjoint(self.entries[pos].concept_uses) and
                   entry.item_defs.isdisjoint(self.entries[pos].item_uses)):
                pos += 1
        entry.order = self._order_before_entry_at(pos)
        entry.save()
        self.entries.insert(pos, entry)
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
            msg = render_template('document/concept_insert_success.html', item=item, category=category)
            msg_entry = DocumentMessageEntry('success', msg, self._order_before_entry_at(pos))
            return [item_entry, msg_entry]
        except FinalItem.DoesNotExist:
            pos = self._pos_for_key(source_id) or 0
            msg_entry = DocumentMessageEntry('warning',
                                             render_template('document/no_defs_found.html', category=category),
                                             self._order_before_entry_at(pos))
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
        item_entry.delete()
        msg_entry = DocumentMessageEntry('success', unicode(item) + " was removed", order,
                                         dict(type = 'delete', entry = item_id))
        return [msg_entry]

    def json_data_for_entries(self, entries):
        category_set = set()
        for entry in entries:
            category_set.update(entry.category_set)
        return dict(items       = [entry.json_data() for entry in entries],
                    concept_map = [(c.id, c.json_data()) for c in category_set])

    def json_data(self):
        return self.json_data_for_entries(self.entries)
