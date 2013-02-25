from django.shortcuts import render
from django.views.decorators.http import require_GET
from items.models import FinalItem
from tags.helpers import clean_tag, normalize_tag
from analysis.models import Concept

@require_GET
def index(request):
    c = {
         'missing_defs': Concept.objects.exclude(refs_to_this=0).filter(defs_for_this=0).all(),
         'finalitems':   list(FinalItem.objects.filter(itemtype='D', status='F').order_by('-created_at')[:5]),
        }
    return render(request, 'definitions/index.html', c) 

@require_GET
def concept_search(request, primary_name):
    primary_name = clean_tag(primary_name)
    primary_norm = normalize_tag(primary_name)
    secondary_names = request.GET.get('tags', '').split(',')
    secondary_names = set(map(clean_tag, secondary_names)) - set([''])
    secondary_norms = map(normalize_tag, secondary_names)
    query = FinalItem.objects.filter(itemtype='D', status='F', finalitemtag__tag__normalized=primary_norm, finalitemtag__primary=True)
    for secondary_norm in set(secondary_norms):
        query = query.filter(finalitemtag__tag__normalized=secondary_norm)
    fitem_list = query.all()
    c = { 'primary':     primary_name,
          'secondaries': secondary_names,
          'result_list': fitem_list }
    return render(request, 'definitions/concept_search.html', c)
