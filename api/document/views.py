from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from api.helpers import api_view
from document.helpers import add_concept_to_document
from document.models import Document

import logging
logger = logging.getLogger(__name__)

@api_view
@require_POST
def add_concept(request, doc_id):
    document = get_object_or_404(Document, pk=doc_id)
    doc_concept_item = add_concept_to_document(document, request.data)
    return doc_concept_item.json_serializable()
