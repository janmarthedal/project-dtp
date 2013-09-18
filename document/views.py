from django.db.models import Max
from django.views.decorators.http import require_safe
from django.shortcuts import render, get_object_or_404
from document.models import Document, DocumentItem
from items.models import FinalItem
from main.helpers import init_context, logged_in_or_404

import logging
logger = logging.getLogger(__name__)

def add_item_to_document(document, item_id):
    item = get_object_or_404(FinalItem, final_id=item_id)
    try:
        DocumentItem.objects.get(document=document, item=item)
        return
    except DocumentItem.DoesNotExist:
        all_items_query = DocumentItem.objects.filter(document=document)
        if all_items_query.count() == 0:
            order = 1
        else: 
            order = all_items_query.aggregate(max=Max('order'))['max'] + 1 
        DocumentItem.objects.create(document=document, item=item, order=order)

@require_safe
@logged_in_or_404
def new(request):
    c = init_context('document')
    document = Document.objects.create(created_by=request.user, title='Unnamed')
    items = filter(None, request.GET.get('items', '').split(' '))
    for item_id in items:
        add_item_to_document(document, item_id)
    return render(request, 'document/view.html', c)

@require_safe
@logged_in_or_404
def add(request, doc_id, item_id):
    c = init_context('document')
    document = get_object_or_404(Document, pk=doc_id, created_by=request.user)
    add_item_to_document(document, item_id)
    return render(request, 'document/view.html', c)

@require_safe
def view(request, doc_id):
    c = init_context('document')
    return render(request, 'document/view.html', c)
