from django.contrib import messages
from django.views.decorators.http import require_POST, require_http_methods
from drafts.models import DraftItem
from items.models import FinalItem
from api.helpers import (itemtype_supported, itemtype_has_parent, ApiError, api_view,
                         api_request_user, api_request_string, api_request_string_list_list)

import logging
logger = logging.getLogger(__name__)

@require_POST
@api_view
def drafts(request):
    user = api_request_user(request)
    itemtype = api_request_string(request, 'type')
    if not itemtype_supported(itemtype):
        raise ValueError('type')
    body = api_request_string(request, 'body')
    primary_categories = api_request_string_list_list(request, 'pricats')
    secondary_categories = api_request_string_list_list(request, 'seccats')
    if itemtype_has_parent(itemtype):
        parent_id = api_request_string(request, 'parent')
        try:
            parent = FinalItem.objects.get(final_id=parent_id)
        except FinalItem.DoesNotExist:
            raise ValueError('parent')
    else:
        parent = None

    item = DraftItem.objects.add_item(user, itemtype, body, primary_categories, secondary_categories, parent)

    message = '{} successfully created'.format(item)
    logger.debug(message)
    messages.success(request, message)

    result = {
        'id': item.pk,
        'type': itemtype,
        'body': body,
        'pricats': primary_categories,
        'seccats': secondary_categories
    }
    if parent:
        result['parent'] = parent.final_id

    return result

@require_http_methods(['PUT'])
@api_view
def drafts_id(request, item_id):
    user = api_request_user(request)
    body = api_request_string(request, 'body')
    primary_categories = api_request_string_list_list(request, 'pricats')
    secondary_categories = api_request_string_list_list(request, 'seccats')

    item = DraftItem.objects.get(pk=item_id)

    if user != item.created_by:
        raise ApiError('Access error')
    if item.status != 'D':
        raise ApiError('Wrong status')

    item.update(body, primary_categories, secondary_categories)

    message = '{} successfully updated'.format(item)
    logger.debug(message)
    messages.success(request, message)

    return {
        'id': item.pk,
        'body': body,
        'pricats': primary_categories,
        'seccats': secondary_categories
    }
