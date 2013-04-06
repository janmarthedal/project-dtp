from django.shortcuts import render
from django.views.decorators.http import require_GET
from items.models import FinalItem
from tags.helpers import clean_tag, normalize_tag
from analysis.models import Concept
from items.helpers import item_search_to_json
from main.helpers import init_context

import logging
logger = logging.getLogger(__name__)

@require_GET
def index(request):
    c = init_context('definitions')
    c['missing_defs'] = Concept.objects.exclude(refs_to_this=0).filter(defs_for_this=0).all()
    c['init_items'] = item_search_to_json(itemtype='D')
    return render(request, 'definitions/index.html', c) 

@require_GET
def concept_search(request, primary_name):
    c = init_context('definitions')
    primary_name = clean_tag(primary_name)
    primary_norm = normalize_tag(primary_name)
    secondary_names = request.GET.get('tags', '').split(',')
    secondary_names = set(map(clean_tag, secondary_names)) - set([''])
    secondary_norms = map(normalize_tag, secondary_names)
    query = FinalItem.objects.filter(itemtype='D', status='F', finalitemtag__tag__normalized=primary_norm, finalitemtag__primary=True)
    for secondary_norm in set(secondary_norms):
        query = query.filter(finalitemtag__tag__normalized=secondary_norm)
    fitem_list = query.all()
    c['primary']     = primary_name
    c['secondaries'] = secondary_names
    c['result_list'] = fitem_list
    return render(request, 'definitions/concept_search.html', c)
