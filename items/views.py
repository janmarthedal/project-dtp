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

@require_http_methods(["GET", "POST"])
def new(request, kind, parent=None):
    if not request.user.is_authenticated():
        messages.info(request, 'You must log in to create a %s' % kind)
        return HttpResponseRedirect('%s?next=%s' % (reverse('users.views.login'), request.path))
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
                item = Item.objects.add_item(request.user, kind, body,
                                             primarytags, othertags, c.get('parent'))
                message = u'%s successfully created' % item
                logger.debug(message)
                messages.success(request, message)
                return HttpResponseRedirect(reverse('items.views.show', args=[item.id]))
            else:  # preview
                c['preview'] = { 'kind':        kind,
                                 'body':        body,
                                 'parent':      c.get('parent'),
                                 'primarytags': primarytags,
                                 'othertags':   othertags }
    c.update(dict(kind=kind, form=form))
    if kind == 'definition':
        c['primary_text'] = 'Terms defined'
    elif kind == 'theorem':
        c['primary_text'] = 'Name(s) of theorem'
    return render(request, 'items/new.html', c)

@login_required
@require_http_methods(["GET", "POST"])
def edit(request, item_id):
    c = {}
    item = get_object_or_404(Item, pk=item_id)
    item_perms = get_user_item_permissions(request.user, item)
    if not item_perms['edit']:
        raise Http404
    if request.method == 'GET':
        form = EditItemForm({ 'body':        item.body,
                              'primarytags': '\n'.join(item.primary_tags),
                              'othertags':   '\n'.join(item.other_tags) })
    else:
        form = EditItemForm(request.POST)
        if form.is_valid():
            primarytags = form.cleaned_data['primarytags']
            othertags   = form.cleaned_data['othertags']
            body        = form.cleaned_data['body']
            if request.POST['submit'].lower() == 'update':
                Item.objects.update_item(item, request.user, body,
                                         primarytags, othertags)
                message = u'%s successfully updated' % item
                logger.debug(message)
                messages.success(request, message)
                return HttpResponseRedirect(reverse('items.views.show', args=[item_id]))
            else:  # preview
                c['preview'] = { 'id':          item.id,
                                 'kind':        item.get_kind_display(),
                                 'body':        body,
                                 'parent':      item.parent,
                                 'primarytags': primarytags,
                                 'othertags':   othertags }
    c.update(dict(item=item, form=form))
    return render(request, 'items/edit.html', c)

@require_safe
def show(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    permissions = get_user_item_permissions(request.user, item)
    if not permissions['view']:
        raise Http404 
    c = { 'item': item,
          'perm': permissions }
    return render(request, 'items/show.html', c)

@require_safe
def show_final(request, final_id):
    item = get_object_or_404(Item, final_id=final_id)
    permissions = get_user_item_permissions(request.user, item)
    c = { 'item': item,
          'perm': permissions }
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

