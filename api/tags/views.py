from django.http import HttpResponse
from django.views.decorators.http import require_GET
from main.helpers import json_encode
from tags.models import Tag

import logging
logger = logging.getLogger(__name__)

@require_GET
def tag_list(request):
    tags = list(Tag.objects.all())
    return HttpResponse(json_encode(tags), content_type="application/json")
