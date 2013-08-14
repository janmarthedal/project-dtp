from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST, require_GET
from items.models import DraftItem, FinalItem
from main.helpers import init_context, logged_in_or_404
from analysis.management.commands.analyze import add_final_item_dependencies, check_final_item_tag_categories

import logging
logger = logging.getLogger(__name__)

def get_user_item_permissions(user, item):
    own_item = user == item.created_by
    logged_in = user.is_authenticated()
    return {
        'view':       (item.status == 'D' and own_item) or item.status == 'R',
        'edit':       item.status == 'D' and own_item,
        'to_draft':   item.status == 'R' and own_item,
        'to_review':  item.status == 'D' and own_item,
        'to_final':   item.status in ['D', 'R'] and own_item,
        'add_proof':  item.status == 'F' and item.itemtype == 'T' and logged_in,
        'add_source': item.status == 'F' and logged_in,
        'edit_final': item.status == 'F' and logged_in,
    }

@require_GET
def new(request, kind, parent=None):
    if not request.user.is_authenticated():
        messages.info(request, "You must be logged in to create a " + kind)
        return HttpResponseRedirect(reverse('users.views.login') + '?next=' + request.path)
    c = init_context(kind)
    if parent:
        if kind != 'proof':
            raise Http404
        c['parent'] = get_object_or_404(FinalItem, final_id=parent, itemtype='T')
    c['kind'] = kind
    if kind == 'definition':
        c['primary_text'] = 'Terms defined'
    elif kind == 'theorem':
        c['primary_text'] = 'Name(s) for theorem'
    return render(request, 'items/new.html', c)

@require_GET
def show(request, item_id):
    item = get_object_or_404(DraftItem, pk=item_id)
    permissions = get_user_item_permissions(request.user, item)
    if not permissions['view']:
        raise Http404
    c = { 'item': item,
          'perm': permissions }
    return render(request, 'items/show.html', c)

@logged_in_or_404
@require_GET
def edit(request, item_id):
    item = get_object_or_404(DraftItem, pk=item_id)
    item_perms = get_user_item_permissions(request.user, item)
    if not item_perms['edit']:
        raise Http404
    c = init_context(item.itemtype)
    c['item'] = item
    if item.itemtype == 'D':
        c['primary_text'] = 'Terms defined'
    elif item.itemtype == 'T':
        c['primary_text'] = 'Name(s) of theorem'
    return render(request, 'items/edit.html', c)

@logged_in_or_404
@require_POST
def delete_draft(request, item_id):
    item = get_object_or_404(DraftItem, pk=item_id)
    if request.user != item.created_by:
        raise Http404
    item.delete()
    return HttpResponseRedirect(reverse('users.views.profile', args=[request.user.get_username()]))

@logged_in_or_404
@require_POST
def to_review(request, item_id):
    item = get_object_or_404(DraftItem, pk=item_id)
    if request.user == item.created_by and item.status == 'D':
        item.make_review()
        return HttpResponseRedirect(reverse('items.views.show', args=[item.id]))
    raise Http404

@logged_in_or_404
@require_POST
def to_final(request, item_id):
    item = get_object_or_404(DraftItem, pk=item_id)

    if request.user != item.created_by or item.status not in ['D', 'R']:
        raise Http404

    fitem = FinalItem.objects.add_item(item)

    add_final_item_dependencies(fitem)
    check_final_item_tag_categories(fitem)

    item.delete()
    return HttpResponseRedirect(reverse('items.views.show_final', args=[fitem.final_id]))

@require_GET
def show_final(request, final_id):
    item = get_object_or_404(FinalItem, final_id=final_id)
    item_perms = get_user_item_permissions(request.user, item)
    validation_count = item.sourcevalidation_set.count()
    proof_count = item.finalitem_set.filter(itemtype='P', status='F').count() if item.itemtype == 'T' else 0
    c = { 'item':             item,
          'perm':             item_perms,
          'validation_count': validation_count,
          'proof_count':      proof_count }
    if validation_count and 'vals' in request.GET:
        c['validation_list'] = item.sourcevalidation_set.all()
    if proof_count and 'prfs' in request.GET:
        c['proof_list'] = item.finalitem_set.filter(itemtype='P', status='F').all()
    return render(request, 'items/show_final.html', c)

@logged_in_or_404
@require_GET
def edit_final(request, final_id):
    item = get_object_or_404(FinalItem, final_id=final_id)
    item_perms = get_user_item_permissions(request.user, item)
    if not item_perms['edit_final']:
        raise Http404
    c = init_context(item.itemtype)
    c['item'] = item
    if item.itemtype == 'D':
        c['primary_text'] = 'Terms defined'
    elif item.itemtype == 'T':
        c['primary_text'] = 'Name(s) of theorem'
    return render(request, 'items/edit_final.html', c)

@logged_in_or_404
@require_POST
def delete_final(request, item_id):
    if not request.user.is_admin:
        raise Http404
    item = get_object_or_404(FinalItem, pk=item_id)
    item.delete()
    return HttpResponseRedirect(reverse('main.views.index'))
