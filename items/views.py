from django.shortcuts import render
from django.views.decorators.http import require_POST, require_safe
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from main.helpers import init_context
from items.models import Item
from items.helpers import prepare_tags, prepare_body, typeset_body, typeset_tag

import logging
logger = logging.getLogger(__name__)

@login_required
def new(request, kind):
    c = init_context(request)
    if request.method == 'POST':
        if request.POST['submit'].lower() == 'save':
            errors = {}
            primary_tag_list = request.POST['primarytags'].splitlines()
            other_tag_list   = request.POST['othertags'].splitlines()
            tags       = prepare_tags(primary_tag_list, other_tag_list, errors)
            body, deps = prepare_body(request.POST['body'], errors)
            if errors:
                c['errors'] = errors
            else:
                item_id = Item.objects.add_item(request.user, kind, body, tags, deps)
                logger.debug('Created %s %d' % (kind, item_id))
                return HttpResponseRedirect(reverse('items.views.show', args=[item_id]))
        for k in ['body', 'primarytags', 'othertags']:
            c[k] = request.POST[k]
    c['kind'] = kind
    return render(request, 'items/new.html', c)

@require_safe
def show(request, item_id):
    c = init_context(request)
    c['id'] = item_id
    try:
        item = Item.objects.get(pk=item_id)
        if item.status == 'R' or (item.status == 'D' and request.user.is_authenticated() and item.created_by.id == request.user.id):
            tags = [(typeset_tag(itemtag.tag.name), itemtag.primary)
                    for itemtag in item.itemtag_set.all()]
            c['kind']         = item.get_kind_display()
            c['status']       = item.get_status_display()
            c['created_by']   = item.created_by.username
            c['modified_at']  = str(item.modified_at)
            c['body']         = typeset_body(item.body)
            c['primary_tags'] = [t[0] for t in tags if t[1]]
            c['other_tags']   = [t[0] for t in tags if not t[1]]
        else:
            c['error'] = 'Access denied'
    except Item.DoesNotExist:
        c['error'] = 'Item does not exist'
    return render(request, 'items/show.html', c)

