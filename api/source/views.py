import json
from django.contrib import messages
from django.views.decorators.http import require_GET, require_POST
from sources.models import RefNode, RefAuthor
from api.helpers import api_view, api_request_user, api_request_string, api_request_string_list

import logging
logger = logging.getLogger(__name__)

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

    return item.json_data()

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

    return [item.json_data() for item in query.all()]
