import json
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from items.helpers import item_search_to_json
from items.models import DraftItem
from tags.models import Tag
from api.helpers import api_view, api_user, api_key, json_response

import logging
logger = logging.getLogger(__name__)

@require_GET
def tags_prefixed(request, prefix):
    tags = Tag.objects.filter(normalized__startswith=prefix).order_by('normalized')[:20]
    response_data = [t.name for t in tags]
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def item_list(request):
    try:
        itemtype = request.GET.get('type')
        status = request.GET.get('status', 'F')
        list_user = None
        user_id = request.GET.get('user')
        if user_id:
            list_user = get_object_or_404(get_user_model(), pk=user_id)
            if status == 'D' and request.user != list_user:
                raise Http404
        include_tags = json.loads(request.GET.get('intags', '[]'))
        exclude_tags = json.loads(request.GET.get('extags', '[]'))
        offset = int(request.GET.get('offset', 0))
        limit  = int(request.GET.get('limit', 5))
    except:
        raise Http404
    result = item_search_to_json(itemtype=itemtype,
                                 include_tag_names=include_tags,
                                 exclude_tag_names=exclude_tags,
                                 status=status,
                                 offset=offset,
                                 limit=limit,
                                 user=list_user)
    return HttpResponse(result, content_type="application/json")

def items(request):
    if request.method == 'GET':
        return item_list(request)
    else:
        raise Http404

@api_view
def drafts_new(request):
    user = api_user(request)
    kind = api_key(request, 'kin')
    body = api_key(request, 'body')
    item = DraftItem.objects.add_item(user, kind, body, None)
    message = u'%s successfully created' % item
    logger.debug(message)
    messages.success(request, message)
    result = {
        'id':   item.pk,
        'body': item.body,
        'kind': item.itemtype
    }
    return json_response(result)

def drafts(request):
    if request.method == 'POST':
        return drafts_new(request)
    else:
        raise Http404
