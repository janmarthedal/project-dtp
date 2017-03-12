from concepts.models import Concept


def prepare_item_view_list(item_iterator):
    return [{
        'item': item,
        'defines': list(Concept.objects.filter(conceptdefinition__item=item)
                            .order_by('name')
                            .values_list('name', flat=True))
    } for item in item_iterator]