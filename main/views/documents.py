from django.db.models import Max, Q
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods, require_safe
from functools import reduce

from concepts.models import Concept, ItemDependency
from documents.models import Document, DocumentItem
from main.views.mathitems import item_render
from mathitems.models import MathItem
from userdata.permissions import Perms, require_perm


@require_perm(Perms.DOCUMENT)
@require_http_methods(['HEAD', 'GET', 'POST'])
def add_item(request, item_name):
    try:
        item = MathItem.objects.get_by_name(item_name)
    except MathItem.DoesNotExist:
        raise Http404('Item does not exist')
    if request.method == 'POST':
        if 'addto' in request.POST:
            document = Document.objects.get(id=int(request.POST['addto']))
        else:
            document = Document.objects.create(created_by=request.user, name='Untitled')
            document.name = 'Document {}'.format(document.pk)
            document.save()
        info = DocumentItem.objects.filter(document=document).aggregate(Max('order'))
        m = info['order__max'] or 0
        DocumentItem.objects.create(document=document, item=item, order=m+10)
        return redirect('doc-show', document.pk)
    return render(request, 'documents/add-item.html', {
        'title': 'Add {} to Document'.format(item.get_name()),
        'documents': Document.objects.filter(created_by=request.user).order_by('created_at'),
    })


@require_safe
def show(request, doc_id):
    try:
        document = Document.objects.get(id=int(doc_id))
    except Document.DoesNotExist:
        raise Http404('Document does not exist')
    return render(request, 'documents/show.html', {
        'title': document.name,
        'items': [{
            'title': str(docitem.item),
            'item_data': item_render(docitem.item),
        } for docitem in DocumentItem.objects.filter(document=document).order_by('order')],
    })


class EntryData:

    def __init__(self, item=None):
        if item:
            self.item_ids = {item.id}
            self.defs = set(Concept.objects.filter(conceptdefinition__item=item)
                            .distinct().values_list('id', flat=True))
            self.conrefs = set(Concept.objects.exclude(name='*')
                               .filter(Q(conceptreference__item=item) | Q(itemdependency__item=item))
                               .distinct().values_list('id', flat=True))
            self.itemrefs = set(ItemDependency.objects.filter(item=item).values_list('uses_id', flat=True))
        else:
            self.item_ids = set()
            self.defs = set()
            self.conrefs = set()
            self.itemrefs = set()

    def union(self, other):
        self.item_ids |= other.item_ids
        self.defs |= other.defs
        self.conrefs |= other.conrefs
        self.itemrefs |= other.itemrefs
        return self


def item_context(item, data, concept_map, item_map):
    return {
        'title': str(item),
        'defines': sorted(concept_map[pk] for pk in data.defs),
        'concept_refs': sorted(concept_map[pk] for pk in data.conrefs),
        'item_refs': sorted(item_map[pk].get_name() for pk in data.itemrefs),
    }


@require_http_methods(['GET', 'POST'])
def edit(request, doc_id):
    try:
        document = Document.objects.get(id=int(doc_id))
    except Document.DoesNotExist:
        raise Http404('Document does not exist')
    docitems = list(MathItem.objects.filter(documentitem__document=document).order_by('documentitem__order'))
    itemdata = {item.pk: EntryData(item) for item in set(docitems)}
    item_map = {item.pk: item for item in set(docitems)}
    alldata = reduce(lambda acc, data: acc.union(data), itemdata.values(), EntryData())
    item_map.update({item.pk: item for item in MathItem.objects.filter(id__in=alldata.itemrefs - set(itemdata.keys()))})
    concept_map = {con.pk: con.name for con in Concept.objects.filter(id__in=alldata.defs | alldata.conrefs)}
    items = [item_context(item, itemdata[item.pk], concept_map, item_map) for item in docitems]
    return render(request, 'documents/edit.html', {
        'title': 'Edit ' + document.name,
        'items': items,
    })
