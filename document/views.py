from django.views.decorators.http import require_safe
from django.shortcuts import render, get_object_or_404
from document.helpers import DocumentView
from document.models import Document
from main.helpers import init_context, logged_in_or_404

import logging
logger = logging.getLogger(__name__)

def view_render(request, document_view):
    c = init_context('document', document=document_view.document, items=document_view.json_serializable())
    return render(request, 'document/view.html', c)

@require_safe
@logged_in_or_404
def new(request):
    document = Document.objects.create(created_by=request.user, title='Unnamed')
    document_view = DocumentView(document)
    items = filter(None, request.GET.get('items', '').split(' '))
    for item_id in items:
        document_view.add_item(item_id)
    return view_render(request, document_view)

@require_safe
@logged_in_or_404
def add(request, doc_id, item_id):
    document = get_object_or_404(Document, pk=doc_id, created_by=request.user)
    document_view = DocumentView(document)
    document_view.add_item(item_id)
    return view_render(request, document_view)

@require_safe
def view(request, doc_id):
    document = get_object_or_404(Document, pk=doc_id, created_by=request.user)
    document_view = DocumentView(document)
    return view_render(request, document_view)
