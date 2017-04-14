from django.db.models import Q

from concepts.models import Concept
from keywords.models import Keyword


def prepare_item_view_list(item_iterator):
    return [{
        'item': item,
        'defines': list(Concept.objects.filter(conceptdefinition__item=item)
                        .distinct()
                        .order_by('name')
                        .values_list('name', flat=True)),
        'refs': list(Concept.objects.exclude(name='*')
                     .filter(Q(conceptreference__item=item) | Q(itemdependency__item=item))
                     .distinct()
                     .order_by('name')
                     .values_list('name', flat=True)),
        'keywords': list(Keyword.objects.filter(itemkeyword__item=item)
                         .order_by('name')
                         .values_list('name', flat=True)),
    } for item in item_iterator]


def prepare_media_view_list(item_iterator):
    return [{
        'item': media,
        'keywords': list(Keyword.objects.filter(mediakeyword__media=media)
                         .order_by('name')
                         .values_list('name', flat=True)),
    } for media in item_iterator]
