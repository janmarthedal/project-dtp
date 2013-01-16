import logging
import re
from django.shortcuts import render
from django.views.decorators.http import require_POST, require_safe
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from main.helpers import init_context
from items.models import Item

logger = logging.getLogger(__name__)

def normalize_tag(name):
    name = name.strip()
    name = re.sub(r' {2,}', r' ', name)
    return name

def prepare_tags(primary_tags, other_tags, errors):
    primary_tags = filter(None, map(normalize_tag, primary_tags))
    other_tags   = filter(None, map(normalize_tag, other_tags))
    intersection = set(primary_tags) & set(other_tags)
    if intersection:
        errors['Duplicate tags'] = intersection
        return None
    else:
        tags = {}
        tags.update(dict.fromkeys(primary_tags, True))
        tags.update(dict.fromkeys(other_tags,   False))
        return tags

def prepare_body(body, errors):
    body = body.strip()
    return body, []

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
                return HttpResponseRedirect(reverse('main.views.index'))
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
            c['kind'] = item.get_kind_display()
        else:
            c['error'] = 'Access denied'
    except Item.DoesNotExist:
        c['error'] = 'Item does not exist'
    return render(request, 'items/show.html', c)

