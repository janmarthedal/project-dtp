from concepts.models import Concept, ConceptDefinition, ConceptReference, ItemDependency, ConceptMeta
from equations.models import Equation, ItemEquation
from mathitems.models import ItemTypes, MathItem, node_to_markup
from media.models import Media
from project.server_com import render_item

# import logging
# logger = logging.getLogger(__name__)


def get_node_refs(node, refs, media_refs):
    if 'item' in node:
        refs.add(node['item'])
    if 'media' in node:
        media_refs.add(node['media'])
    for child in node.get('children', []):
        get_node_refs(child, refs, media_refs)


def get_document_refs(document):
    item_names = set()
    media_names = set()
    get_node_refs(document, item_names, media_names)
    item_info = {}
    for item_name in item_names:
        try:
            item = MathItem.objects.get_by_name(item_name)
            data = {'url': item.get_absolute_url()}
            if item.item_type == ItemTypes.DEF:
                data['defines'] = list(Concept.objects.filter(conceptdefinition__item=item)
                                       .values_list('name', flat=True))
            item_info[item_name] = data
        except MathItem.DoesNotExist:
            pass
    media_info = {}
    for media_name in media_names:
        try:
            media = Media.objects.get_by_name(media_name)
            media_info[media_name] = media.get_html()
        except Media.DoesNotExist:
            pass
    return item_info, media_info


def get_refs_and_render(item_type, document, eqns, concepts):
    refs, media_refs = get_document_refs(document)
    return render_item(item_type, document, eqns, concepts, refs, media_refs)


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

    return concept_defs | concept_refs


def item_to_markup(item):
    eqns, concept_defs, concept_refs, item_refs = item.analyze()
    concepts = concept_defs | concept_refs
    for data in item_refs.values():
        concepts |= data.get('concepts', set())
    concept_map = {id: Concept.objects.get(id=id).name for id in concepts}
    eqn_map = {id: Equation.objects.get(id=id).to_markup() for id in eqns}
    return node_to_markup(item.get_body_root(), concept_map, eqn_map)


def create_concept_meta(concept_id):
    ConceptMeta.objects.update_or_create(
        concept_id=concept_id,
        defaults={
            'ref_count': ConceptReference.objects.filter(concept_id=concept_id).count(),
            'def_count': ConceptDefinition.objects.filter(concept_id=concept_id).count()
        }
    )
