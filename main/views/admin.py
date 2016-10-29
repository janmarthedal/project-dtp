import re
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_safe

from mathitems.models import MathItem
from validations.models import ItemValidation


def itemvalidation_data(itemvalidation):
    return {
        'type': itemvalidation.source.source_type,
        'value': itemvalidation.source.source_value,
        'location': itemvalidation.location
    }

def mathitem_data(item):
    result = {
        'id': item.get_name(),
        'type': item.item_type,
        'body': re.sub('[\n]{3,}', '\n\n', item.to_source().strip()),
        'refs': [itemvalidation_data(itemvalidation)
                 for itemvalidation in item.itemvalidation_set.all()]
    }
    if item.parent:
        result['parent'] = item.parent.get_name()
    return result

@require_safe
def datadump(request):
    items = [mathitem_data(item) for item in MathItem.objects.order_by('id')]
    return JsonResponse({
        'timestamp': datetime.utcnow().isoformat(),
        'itemCount': len(items),
        'items': items,
    })
