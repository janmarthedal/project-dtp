import json
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from tags.models import Tag
from items.helpers import item_search_to_json

import logging
logger = logging.getLogger(__name__)


@require_GET
def tags_prefixed(request, prefix):
    tags = Tag.objects.filter(normalized__startswith=prefix).order_by('normalized')[:20]
    response_data = [t.name for t in tags]
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@require_GET
def item_list(request):
    include_tags = json.loads(request.GET.get('intags', '[]'))
    exclude_tags = json.loads(request.GET.get('extags', '[]'))
    result = item_search_to_json(itemtype=request.GET.get('type', None),
                                 include_tag_names=include_tags,
                                 exclude_tag_names=exclude_tags)
    return HttpResponse(result, content_type="application/json")
