from django.shortcuts import render
from django.views.decorators.http import require_safe

from concepts.models import Concept
from mathitems.models import MathItem
from main.views.helpers import prepare_item_view_list


@require_safe
def show_concept(request, name):
    items = MathItem.objects.filter(conceptdefinition__concept__name=name).order_by('id')
    return render(request, 'concepts/show.html', {
        'title': name,
        'concept_name': name,
        'items': prepare_item_view_list(items),
    })

@require_safe
def list_concepts(request):
    return render(request, 'concepts/list.html', {
        'title': 'All concepts',
        'concepts': Concept.objects.filter(conceptmeta__def_count__gt=0).order_by('name')
    })
