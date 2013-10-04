from django.views.decorators.http import require_GET
from main.helpers import json_response
from tags.models import Tag

import logging
logger = logging.getLogger(__name__)

@require_GET
def tag_list(request):
    tags = list(Tag.objects.all())
    return json_response(tags)
