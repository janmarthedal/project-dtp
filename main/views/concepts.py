from django.shortcuts import render
from django.views.decorators.http import require_safe

from concepts.models import MathItem
from main.views.helpers import prepare_item_view_list


@require_safe
def show_concept(request, name):
    return render(request, 'concepts/show.html', {
        'title': name,
        'items': prepare_item_view_list(MathItem.objects.filter(conceptdefinition__concept__name=name).order_by('id')),
    })
