from mathitems.models import Concept, ItemTypes, MathItem
from project.server_com import render_item


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

def get_refs_and_render(item_type, document, eqns):
    refs = get_document_refs(document)
    return render_item(item_type, document, eqns, refs)
