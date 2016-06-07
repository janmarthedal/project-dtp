from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_safe

from mathitems.models import MathItem, ItemTypes

import logging
logger = logging.getLogger(__name__)


@require_safe
def show_item(request, id_str):
    item = MathItem.objects.get_by_name(id_str)
    item_data = item.render()
    if item_data['errors']:
        logger.warn('Error in published item {}'.format(item.id))
    del item_data['errors']
    context = {
        'title': str(item),
        'item_data': item_data,
    }
    if item.item_type == ItemTypes.THM:
        context['new_proof_link'] = reverse('new-prf', args=[item.get_name()])
    return render(request, 'mathitems/show.html', context)


def item_home(request, item_type, new_draft_url=None):
    name = ItemTypes.NAMES[item_type]
    items = MathItem.objects.filter(item_type=item_type).order_by('-created_at')
    context = {
        'title': name,
        'items': items,
    }
    if new_draft_url:
        context.update(new_name='New ' + name, new_url=new_draft_url)
    return render(request, 'mathitems/item-home.html', context)


@require_safe
def def_home(request):
    return item_home(request, ItemTypes.DEF, reverse('new-def'))


@require_safe
def thm_home(request):
    return item_home(request, ItemTypes.THM, reverse('new-thm'))


@require_safe
def prf_home(request):
    return item_home(request, ItemTypes.PRF)
