from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST, require_http_methods
from api.helpers import api_view
from document.helpers import DocumentView
from document.models import Document
from main.helpers import logged_in_or_404

import logging
logger = logging.getLogger(__name__)

@require_POST
@logged_in_or_404
@api_view
def add_concept(request, doc_id):
    document = get_object_or_404(Document, pk=doc_id, created_by=request.user)
    document_view = DocumentView(document)
    tag_list = request.data['concept']
    source_id = request.data['source_id']
    new_entries = document_view.add_concept(tag_list, source_id)
    return document_view.json_data_for_entries(new_entries)

@require_POST
@logged_in_or_404
@api_view
def add_item(request, doc_id):
    document = get_object_or_404(Document, pk=doc_id, created_by=request.user)
    document_view = DocumentView(document)
    item_id = request.data['item_id']
    source_id = request.data['source_id']
    new_entries = document_view.add_item(item_id, source_id)
    return document_view.json_data_for_entries(new_entries)

@require_POST
@logged_in_or_404
@api_view
def delete(request, doc_id):
    document = get_object_or_404(Document, pk=doc_id, created_by=request.user)
    document_view = DocumentView(document)
    new_entries = document_view.delete(request.data)
    return document_view.json_data_for_entries(new_entries)

@require_http_methods(['PUT'])
@logged_in_or_404
@api_view
def sync(request, doc_id):
    document = get_object_or_404(Document, pk=doc_id, created_by=request.user)
    if 'title' in request.data:
        document.title = request.data['title']
    document.save()
    return document.json_data()
