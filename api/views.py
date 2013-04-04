import json
from django.http import HttpResponse
from tags.models import Tag

import logging
logger = logging.getLogger(__name__)


def tags_prefixed(request, prefix):
    logger.debug("tags_prefixed '%s'" % prefix)
    tags = Tag.objects.filter(normalized__startswith=prefix).order_by('normalized')[:20]
    response_data = [t.name for t in tags]
    return HttpResponse(json.dumps(response_data), content_type="application/json")
