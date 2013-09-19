from django.contrib.auth import get_user_model
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_http_methods
from items.helpers import item_search_to_json
from items.models import FinalItem
from main.helpers import json_decode
from api.helpers import (ApiError, api_view, api_request_user, api_request_string_list_list,
                         api_request_tag_category_list)

import logging
logger = logging.getLogger(__name__)

@require_GET
def items(request):
    try:
        itemtype = request.GET.get('type')
        status = request.GET.get('status', 'F')
        parent = request.GET.get('parent')
        list_user = None
        user_id = request.GET.get('user')
        category = request.GET.get('category')
        if user_id:
            list_user = get_object_or_404(get_user_model(), pk=user_id)
            if status == 'D' and request.user != list_user:
                raise Http404
        include_tags = json_decode(request.GET.get('intags', '[]'))
        exclude_tags = json_decode(request.GET.get('extags', '[]'))
        offset = int(request.GET.get('offset', 0))
        limit  = int(request.GET.get('limit', 5))
    except:
        raise Http404
    result = item_search_to_json(itemtype=itemtype,
                                 parent=parent,
                                 include_tag_names=include_tags,
                                 exclude_tag_names=exclude_tags,
                                 category=category,
                                 status=status,
                                 offset=offset,
                                 limit=limit,
                                 user=list_user)
    return HttpResponse(result, content_type="application/json")

@require_http_methods(['PUT'])
@api_view
def final_id(request, item_id):
    user = api_request_user(request)
    # TODO: Check user has permission to update final item

    primary_categories = api_request_string_list_list(request, 'pricats')
    secondary_categories = api_request_string_list_list(request, 'seccats')
    tag_category_map = api_request_tag_category_list(request, 'tagcatmap')

    item = FinalItem.objects.get(final_id=item_id)

    if item.status != 'F':
        raise ApiError('Wrong status')

    item.update(user, primary_categories, secondary_categories, tag_category_map)

    return {
        'id':        item.final_id,
        'pricats':   primary_categories,
        'seccats':   secondary_categories,
        'tagcatmap': tag_category_map
    }
