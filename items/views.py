from collections import Counter
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST, require_safe, require_http_methods
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.template.loader import get_template
from django.template import Context
from django import forms
from main.helpers import init_context, datetime_user_string
from items.models import Item
from items.helpers import normalize_tag, make_short_name

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
        'add_proof':  item.status == 'F' and item.kind == 'T' and logged_in,
        'add_source': item.status == 'F' and logged_in,
        }    

class TagListField(forms.CharField):

    def __init__(self, *args, **kwargs):
        super(TagListField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(TagListField, self).clean(value)
        tag_list = filter(None, map(normalize_tag, value.splitlines()))
        return tag_list

class EditItemForm(forms.Form):
    body        = forms.CharField(widget=forms.Textarea(attrs={'class': 'body'}), required=False)
    primarytags = TagListField(widget=forms.Textarea(attrs={'class': 'tags'}), required=False)
    othertags   = TagListField(widget=forms.Textarea(attrs={'class': 'tags'}), required=False)

    def clean_body(self):
        return self.cleaned_data['body'].strip()

    def clean(self):
        cleaned_data = super(EditItemForm, self).clean()
        primarytags = cleaned_data['primarytags']
        othertags   = cleaned_data['othertags']
        tag_counter = Counter(primarytags) + Counter(othertags)
        duplicates = [p[0] for p in tag_counter.iteritems() if p[1] > 1]
        if duplicates:
            t = get_template('inline/taglist.html')
            c = Context({ 'header':  'Tag duplicates:',
                          'taglist': duplicates })
            raise ValidationError([t.render(c)])
        return cleaned_data

@login_required
@require_http_methods(["GET", "POST"])
def new(request, kind, parent=None):
    c = {}
    if parent:
        if kind != 'proof':
            raise Http404
        c['parent'] = get_object_or_404(Item, final_id=parent, kind='T')
    if request.method == 'GET':
        form = EditItemForm()
    else:
        form = EditItemForm(request.POST)
        if form.is_valid():
            primarytags = form.cleaned_data['primarytags']
            othertags   = form.cleaned_data['othertags']
            body        = form.cleaned_data['body']
            if request.POST['submit'].lower() == 'save':
                item_id = Item.objects.add_item(request.user, kind, body,
                                                primarytags, othertags, c['parent'])
                message = '%s %s successfully created' % (kind.capitalize(), str(item_id))
                logger.debug(message)
                messages.success(request, message)
                return HttpResponseRedirect(reverse('items.views.show', args=[item_id]))
            else:  # preview
                c['preview'] = { 'kind':        kind,
                                 'body':        body,
                                 'parent':      c['parent'],
                                 'primarytags': primarytags,
                                 'othertags':   othertags }
    c.update(dict(kind=kind, form=form))
    return render(request, 'items/new.html', c)

@login_required
@require_http_methods(["GET", "POST"])
def edit(request, item_id):
    c = {}
    item = get_object_or_404(Item, pk=item_id)
    item_perms = get_user_item_permissions(request.user, item)
    if not item_perms['edit']:
        raise Http404
    tags = [(itemtag.tag.name, itemtag.primary)
            for itemtag in item.itemtag_set.all()]
    primarytags = [t[0] for t in tags if t[1]]
    othertags   = [t[0] for t in tags if not t[1]]
    if request.method == 'GET':
        form = EditItemForm({ 'body':        item.body,
                              'primarytags': '\n'.join(primarytags),
                              'othertags':   '\n'.join(othertags) })
    else:
        form = EditItemForm(request.POST)
        if form.is_valid():
            newprimarytags = form.cleaned_data['primarytags']
            newothertags   = form.cleaned_data['othertags']
            newbody        = form.cleaned_data['body']
            if request.POST['submit'].lower() == 'update':
                Item.objects.update_item(item, request.user, newbody,
                                         newprimarytags, newothertags)
                message = '%s %s successfully updated' % (item.get_kind_display().capitalize(), str(item_id))
                logger.debug(message)
                messages.success(request, message)
                return HttpResponseRedirect(reverse('items.views.show', args=[item_id]))
            else:  # preview
                c['preview'] = { 'id':          item.id,
                                 'kind':        item.get_kind_display(),
                                 'body':        newbody,
                                 'parent':      item.parent,
                                 'primarytags': newprimarytags,
                                 'othertags':   newothertags }
    c.update(dict(item=item, form=form))
    return render(request, 'items/edit.html', c)

@require_safe
def show(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    permissions = get_user_item_permissions(request.user, item)
    if not permissions['view']:
        raise Http404 
    tags = [(itemtag.tag.name, itemtag.primary)
            for itemtag in item.itemtag_set.all()]
    c = {
        'modified_at':  datetime_user_string(request.user, item.modified_at),
        'primary_tags': [t[0] for t in tags if t[1]],
        'other_tags':   [t[0] for t in tags if not t[1]],
        'item':         item,
        'perm':         permissions
        }
    return render(request, 'items/show.html', c)

@require_safe
def show_final(request, final_id):
    item = get_object_or_404(Item, final_id=final_id)
    permissions = get_user_item_permissions(request.user, item)
    tags = [(itemtag.tag.name, itemtag.primary)
            for itemtag in item.itemtag_set.all()]
    c = {
        'published_at': datetime_user_string(request.user, item.final_at),
        'primarytags':  [t[0] for t in tags if t[1]],
        'othertags':    [t[0] for t in tags if not t[1]],
        'item':         item,
        'perm':         permissions,
        }
    return render(request, 'items/show_final.html', c)

@login_required
@require_POST
def change_status(request):
    item_id = request.POST['item']
    item = get_object_or_404(Item, pk=item_id)
    own_item = request.user.is_authenticated() and request.user == item.created_by
    if request.POST['status'] == 'publish':
        if not own_item or item.status not in ['D', 'R']:
            raise Http404 
        item.make_final(request.user)
        return HttpResponseRedirect(reverse('items.views.show_final', args=[item.final_id]))
    else:
        if not own_item or item.status != 'D':
            raise Http404 
        item.make_review(request.user)
        return HttpResponseRedirect(reverse('items.views.show', args=[item.id]))

