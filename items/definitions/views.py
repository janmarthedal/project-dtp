from django.shortcuts import render
from django.views.decorators.http import require_GET
from items.helpers import item_search_to_json
from main.helpers import init_context

import logging
logger = logging.getLogger(__name__)

@require_GET
def index(request):
    c = init_context('definitions')
    c['init_items'] = item_search_to_json(itemtype='D')
    return render(request, 'definitions/index.html', c)
