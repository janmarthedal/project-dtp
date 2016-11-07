from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_safe

from main.item_helpers import item_to_markup
from mathitems.models import MathItem


@require_safe
def datadump(request):
    return HttpResponse(''.join(render_to_string('mathitems/dump.txt', {
        'item': item,
        'markup': item_to_markup(item),
        'validations': item.itemvalidation_set.all()
    }) for item in MathItem.objects.order_by('id')), content_type="text/plain")
