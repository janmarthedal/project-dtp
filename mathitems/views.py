from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_safe

from mathitems.models import MathItem, ItemTypes

import logging
logger = logging.getLogger(__name__)


def show_item(request, id_str, item_type):
    item = get_object_or_404(MathItem, id=int(id_str), item_type=item_type)
    item_data = item.render()
    if item_data['errors']:
        logger.warn('Error in published item {}'.format(item.id))
    del item_data['errors']
    return render(request, 'mathitems/show.html', {
        'title': str(item),
        'item_data': item_data,
    })

@require_safe
def show_def(request, id_str):
    return show_item(request, id_str, ItemTypes.DEF)

@require_safe
def show_thm(request, id_str):
    return show_item(request, id_str, ItemTypes.THM)

def item_home(request, item_type, new_draft_url):
    name = ItemTypes.NAMES[item_type]
    items = MathItem.objects.filter(item_type=item_type).order_by('-created_at')
    return render(request, 'mathitems/item-home.html', {
        'title': name,
        'new_name': 'New ' + name,
        'new_url': new_draft_url,
        'items': items,
    })

@require_safe
def def_home(request):
    return item_home(request, ItemTypes.DEF, reverse('new-def'))

@require_safe
def thm_home(request):
    return item_home(request, ItemTypes.THM, reverse('new-thm'))
