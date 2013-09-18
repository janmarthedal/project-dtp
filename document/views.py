from django.views.decorators.http import require_safe
from django.shortcuts import render, get_object_or_404
from document.helpers import add_item_to_document
from document.models import Document, DocumentItem
from items.models import ItemTagCategory
from main.helpers import init_context, logged_in_or_404

import logging
logger = logging.getLogger(__name__)

def view_render(request, document):
    items = []
    for doc_item in DocumentItem.objects.filter(document=document).all():
        item = doc_item.item
        tag_to_category_map = {}
        for item_tag_category in ItemTagCategory.objects.filter(item=item).all():
            tag = item_tag_category.tag.name
            category = item_tag_category.category.get_tag_list()
            tag_to_category_map[tag] = category
        items.append(dict(type    = 'item',
                          item_id = item.final_id,
                          name    = unicode(item),
                          body    = item.body,
                          order   = doc_item.order,
                          tag_map = tag_to_category_map))
    c = init_context('document', document=document, items=items)
    return render(request, 'document/view.html', c)

@require_safe
@logged_in_or_404
def new(request):
    document = Document.objects.create(created_by=request.user, title='Unnamed')
    items = filter(None, request.GET.get('items', '').split(' '))
    for item_id in items:
        add_item_to_document(document, item_id)
    return view_render(request, document)

@require_safe
@logged_in_or_404
def add(request, doc_id, item_id):
    document = get_object_or_404(Document, pk=doc_id, created_by=request.user)
    add_item_to_document(document, item_id)
    return view_render(request, document)

@require_safe
def view(request, doc_id):
    document = get_object_or_404(Document, pk=doc_id, created_by=request.user)
    return view_render(request, document)
