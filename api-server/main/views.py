import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from main.models import DraftItem, MathItem

@require_http_methods(['GET', 'POST'])
def drafts(request):
    if request.method == 'GET':
        ids = list(DraftItem.objects.order_by('id').values_list('id', flat=True))
        return JsonResponse({'ids': ids})
    else:
        data = json.loads(request.body.decode())
        item_type = {long: short for short, long in MathItem.MATH_ITEM_TYPES}[data['type']]
        item = DraftItem.objects.create(item_type=item_type, body=data['body'])
        return JsonResponse({'id': item.id})
