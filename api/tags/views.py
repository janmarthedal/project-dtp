from django.http import HttpResponse
from django.views.decorators.http import require_GET
from main.helpers import json_encode
from tags.models import Tag

import logging
logger = logging.getLogger(__name__)

@require_GET
def tags_prefixed(request, prefix):
    tags = list(Tag.objects.filter(normalized__startswith=prefix).order_by('normalized')[:20])
    return HttpResponse(json_encode(tags), content_type="application/json")
