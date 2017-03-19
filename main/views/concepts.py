from django.shortcuts import render
from django.views.decorators.http import require_safe

from concepts.models import MathItem
from main.views.helpers import prepare_item_view_list


@require_safe
def show_concept(request, name):
    items = MathItem.objects.filter(conceptdefinition__concept__name=name).order_by('id')
    return render(request, 'concepts/show.html', {
        'title': name,
        'concept_name': name,
        'items': prepare_item_view_list(items),
    })
