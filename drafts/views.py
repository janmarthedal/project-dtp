from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST, require_GET
from api.helpers import itemtype_has_parent
from drafts.models import DraftItem
from items.helpers import publishIssues, get_primary_text
from items.models import FinalItem
from main.helpers import init_context, logged_in_or_404
from analysis.management.commands.deps import add_final_item_dependencies, check_final_item_tag_categories

import logging
logger = logging.getLogger(__name__)

@require_GET
def new(request, kind, parent=None):
    if not request.user.is_authenticated():
        messages.info(request, 'You must be logged in to create a ' + kind)
        return HttpResponseRedirect(reverse('users.views.login') + '?next=' + request.path)
    type_key = DraftItem.type_name_to_type_key(kind)
    if parent:
        cancel_link=reverse('items.views.show_final', args=[parent])
    elif type_key == 'D':
        cancel_link=reverse('items.definitions.views.index')
    elif type_key == 'T':
        cancel_link=reverse('items.theorems.views.index')
    else:
        assert False
    c = init_context(kind, primary_text=get_primary_text(type_key), kind=kind,
                     cancel_link=cancel_link)
    if parent:
        if not itemtype_has_parent(kind):
            raise Http404
        c['parent'] = get_object_or_404(FinalItem, final_id=parent, itemtype='T')
    return render(request, 'drafts/new_draft.html', c)

@require_GET
def edit(request, item_id):
    item = get_object_or_404(DraftItem, pk=item_id)
    if not request.user.has_perm('edit', item):
        raise Http404
    c = init_context(item.itemtype, item=item, primary_text=get_primary_text(item.itemtype))
    return render(request, 'drafts/edit_draft.html', c)

@require_GET
def show(request, item_id):
    item = get_object_or_404(DraftItem, pk=item_id)
    if not request.user.has_perm('view', item):
        raise Http404
    c = {'item': item, 'validations': [v.json_data() for v in item.draftvalidation_set.all()],
         'allow': {p: request.user.has_perm(p, item)
                   for p in ['to_draft', 'to_review', 'to_final', 'add_source', 'edit', 'delete']}}
    return render(request, 'drafts/show_draft.html', c)

@logged_in_or_404
@require_POST
def delete(request, item_id):
    item = get_object_or_404(DraftItem, pk=item_id)
    if request.user != item.created_by:
        raise Http404
    item.delete()
    return HttpResponseRedirect(reverse('users.views.profile', args=[request.user.get_username()]))

@logged_in_or_404
@require_POST
def to_draft(request, item_id):
    item = get_object_or_404(DraftItem, pk=item_id)
    if not request.user.has_perm('to_draft', item):
        raise Http404
    item.make_draft()
    return HttpResponseRedirect(reverse('drafts.views.show', args=[item.id]))

@logged_in_or_404
@require_POST
def to_review(request, item_id):
    item = get_object_or_404(DraftItem, pk=item_id)
    if not request.user.has_perm('to_review', item):
        raise Http404
    item.make_review()
    return HttpResponseRedirect(reverse('drafts.views.show', args=[item.id]))

@logged_in_or_404
@require_POST
def to_final(request, item_id):
    item = get_object_or_404(DraftItem, pk=item_id)
    if not request.user.has_perm('to_final', item):
        raise Http404
    publish_issues = publishIssues(item)
    if publish_issues:
        for issue in publish_issues:
            messages.warning(request, 'Unable to publish: %s' % issue)
        return HttpResponseRedirect(reverse('drafts.views.show', args=[item_id]))
    else:
        fitem = FinalItem.objects.add_item(item)
        add_final_item_dependencies(fitem)
        check_final_item_tag_categories(fitem)
        item.delete()
        messages.success(request, '%s successfully published' % fitem)
        return HttpResponseRedirect(reverse('items.views.edit_final', args=[fitem.final_id]))
