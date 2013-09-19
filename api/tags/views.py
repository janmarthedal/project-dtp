import json
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from items.helpers import item_search_to_json
from drafts.models import DraftItem
from items.models import FinalItem
from main.helpers import json_decode, json_encode
from tags.models import Tag
from sources.models import RefNode, RefAuthor
from api.helpers import (ApiError, api_view, api_request_user, api_request_string, api_request_string_list,
                         api_request_string_list_list, api_request_tag_category_list)

import logging
logger = logging.getLogger(__name__)

@require_GET
def tags_prefixed(request, prefix):
    tags = list(Tag.objects.filter(normalized__startswith=prefix).order_by('normalized')[:20])
    return HttpResponse(json_encode(tags), content_type="application/json")

def item_list(request):
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

def items(request):
    if request.method == 'GET':
        return item_list(request)
    else:
        raise Http404

def itemtype_supported(itemtype):
    return itemtype in ['definition', 'theorem', 'proof']

def itemtype_has_parent(itemtype):
    return itemtype in ['proof']

###########################################################
# Drafts
###########################################################

@api_view
def drafts_new(request):
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

    message = u'%s successfully created' % item
    logger.debug(message)
    messages.success(request, message)

    result = {
        'id':      item.pk,
        'type':    itemtype,
        'body':    body,
        'pricats': primary_categories,
        'seccats': secondary_categories
    }
    if parent:
        result['parent'] = parent.final_id

    return result

@api_view
def drafts_save(request, item_id):
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

    message = u'%s successfully updated' % item
    logger.debug(message)
    messages.success(request, message)

    result = {
        'id':      item.pk,
        'body':    body,
        'pricats': primary_categories,
        'seccats': secondary_categories
    }

    return result

def drafts(request):
    if request.method == 'POST':
        return drafts_new(request)
    else:
        raise Http404

def drafts_id(request, item_id):
    if request.method == 'PUT':
        return drafts_save(request, item_id)
    else:
        raise Http404

###########################################################
# Final
###########################################################

@api_view
def final_save(request, item_id):
    user = api_request_user(request)
    # TODO: Check user has permission to update final item

    primary_categories = api_request_string_list_list(request, 'pricats')
    secondary_categories = api_request_string_list_list(request, 'seccats')
    tag_category_map = api_request_tag_category_list(request, 'tagcatmap')

    item = FinalItem.objects.get(final_id=item_id)

    if item.status != 'F':
        raise ApiError('Wrong status')

    item.update(user, primary_categories, secondary_categories, tag_category_map)

    result = {
        'id':        item.final_id,
        'pricats':   primary_categories,
        'seccats':   secondary_categories,
        'tagcatmap': tag_category_map
    }
    return result

def final_id(request, item_id):
    if request.method == 'PUT':
        return final_save(request, item_id)
    raise Http404

###########################################################
# Source
###########################################################

def api_string_clean(request, key):
    try:
        return api_request_string(request, key).strip() or None
    except KeyError:
        return None

def api_string_list_clean(request, key):
    try:
        return filter(None, map(lambda st: st.strip(), api_request_string_list(request, key)))
    except KeyError:
        return []

@api_view
@require_POST
def source(request):
    item = RefNode(created_by=api_request_user(request),
                   sourcetype=api_request_string(request, 'type'))
    for key in RefNode.STRING_FIELDS:
        item.__dict__[key] = api_string_clean(request, key)
    item.save()

    item.authors = map(lambda n: RefAuthor.objects.get_or_create(name=n)[0], api_string_list_clean(request, 'author'))
    item.editors = map(lambda n: RefAuthor.objects.get_or_create(name=n)[0], api_string_list_clean(request, 'editor'))
    item.save()

    message = u'%s successfully created' % item
    logger.debug(message)
    messages.success(request, message)

    return item.json_serializable()

@api_view
@require_GET
def source_search(request):
    if not any([key in request.data for key in ['title', 'author']]):
        return []
    query = RefNode.objects

    value = api_string_clean(request, 'title')
    if value:
        query = query.filter(title__istartswith=value)

    value = api_string_clean(request, 'author')
    if value:
        names = filter(None, map(lambda st: st.strip(), json.loads(value)))
        for name in names:
            query = query.filter(authors__name__istartswith=name)

    return [item.json_serializable() for item in query.all()]
