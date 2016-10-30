from concepts.models import Concept, ConceptDefinition, ConceptReference, ItemDependency
from equations.models import ItemEquation
from mathitems.models import ItemTypes, MathItem
from project.server_com import render_item

#import logging
#logger = logging.getLogger(__name__)

def get_node_refs(node, refs):
    if 'item' in node:
        refs.add(node['item'])
    for child in node.get('children', []):
        get_node_refs(child, refs)

def get_document_refs(document):
    item_names = set()
    get_node_refs(document, item_names)
    info = {}
    for item_name in item_names:
        try:
            item = MathItem.objects.get_by_name(item_name)
            data = {'url': item.get_absolute_url()}
            if item.item_type == ItemTypes.DEF:
                data['defines'] = list(Concept.objects.filter(conceptdefinition__item=item)
                                            .values_list('name', flat=True))
            info[item_name] = data
        except MathItem.DoesNotExist:
            pass
    return info

def get_refs_and_render(item_type, document, eqns, concepts):
    refs = get_document_refs(document)
    return render_item(item_type, document, eqns, concepts, refs)


def create_item_meta_data(item):
    eqns, concept_defs, concept_refs, item_refs = item.analyze()

    wildcard_concept = Concept.objects.get(name='*')

    if item.item_type == ItemTypes.DEF:
        ConceptDefinition.objects.bulk_create(
            ConceptDefinition(item=item, concept_id=id)
            for id in concept_defs)

    ConceptReference.objects.bulk_create(
        ConceptReference(item=item, concept_id=id)
        for id in concept_refs)

    for item_id, item_data in item_refs.items():
        dest_item = MathItem.objects.get_by_name(item_id)
        dep = ItemDependency.objects.create(item=item, uses=dest_item)
        if dest_item.is_def():
            concepts = list(item_data.get('concepts', []))
            if item_data.get('whole'):
                concepts.append(wildcard_concept.id)
            dep.concepts = concepts

    ItemEquation.objects.bulk_create(
        ItemEquation(item=item, equation_id=id)
        for id in eqns)
