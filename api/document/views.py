from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
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
    concept_entry = document_view.add_concept(request.data)
    return document_view.json_data_for_entries([concept_entry])
