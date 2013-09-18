from django.db.models import Max
from django.shortcuts import get_object_or_404
from document.models import DocumentItem, DocumentConceptItem
from items.models import FinalItem
from tags.models import Category

def max_doc_item_order(document, doc_item_class):
    all_items_query = doc_item_class.objects.filter(document=document)
    if all_items_query.count() == 0:
        return 0
    return all_items_query.aggregate(max=Max('order'))['max'] 

def append_order(document):
    return max(max_doc_item_order(document, DocumentItem),
               max_doc_item_order(document, DocumentConceptItem)) + 1

def add_item_to_document(document, item_id):
    item = get_object_or_404(FinalItem, final_id=item_id)
    try:
        doc_item = DocumentItem.objects.get(document=document, item=item)
    except DocumentItem.DoesNotExist:
        order = append_order(document)
        doc_item = DocumentItem.objects.create(document=document, item=item, order=order)
    return doc_item

def add_concept_to_document(document, tag_list):
    category = Category.objects.from_tag_list(tag_list)
    try:
        doc_item = DocumentConceptItem.objects.get(document=document, category=category)
    except DocumentConceptItem.DoesNotExist:
        order = append_order(document)
        doc_item = DocumentConceptItem.objects.create(document=document, category=category, order=order)
    return doc_item
    