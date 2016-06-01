from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_safe

from mathitems.models import MathItem, ItemTypes, item_to_html


def show_item(request, id_str, item_type):
    item = get_object_or_404(MathItem, id=int(id_str), item_type=item_type)
    item_data = item_to_html(item)
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
