import json
from django.http import HttpResponse
from tags.models import Tag


def tags_prefixed(request, prefix):
    tags = Tag.objects.filter(normalized__startswith=prefix).order_by('normalized')[:20]
    response_data = [t.name for t in tags]
    return HttpResponse(json.dumps(response_data), content_type="application/json")
