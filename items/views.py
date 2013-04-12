from collections import Counter
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.template.loader import get_template
from django.template import Context
from django import forms
from items.models import DraftItem, FinalItem
from items.helpers import BodyScanner, TagListField
from analysis.models import add_final_item_dependencies

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
        }    


class EditItemForm(forms.Form):
    body          = forms.CharField(widget=forms.Textarea(attrs={'class': 'item-body span12'}), required=False)
    primarytags   = TagListField(widget=forms.Textarea(attrs={'class': 'tags', 'rows': 5 }), required=False)
    secondarytags = TagListField(widget=forms.Textarea(attrs={'class': 'tags', 'rows': 5 }), required=False)

    def clean_body(self):
        return self.cleaned_data['body'].strip()

    def clean(self):
        self.pre_validate = super(EditItemForm, self).clean()
        errors = []
        # check tags
        primarytags   = self.pre_validate['primarytags']
        secondarytags = self.pre_validate['secondarytags']
        tag_counter = Counter(primarytags) + Counter(secondarytags)
        duplicates = [p[0] for p in tag_counter.iteritems() if p[1] > 1]
        if duplicates:
            t = get_template('inline/taglist.html')
            c = Context({ 'header':  'Tag duplicates:',
                          'taglist': duplicates })
            errors.append(t.render(c))
        # check body
        self.bodyscan = BodyScanner(self.pre_validate['body'])
        for final_id in set(self.bodyscan.getItemRefList()):
            try:
                FinalItem.objects.get(final_id=final_id, status='F')
            except FinalItem.DoesNotExist:
                errors.append('Reference %s does not exist' % final_id)
        if errors:
            raise ValidationError(errors)
        return self.pre_validate


@require_http_methods(["GET", "POST"])
def new(request, kind, parent=None):
    if not request.user.is_authenticated():
        messages.info(request, 'You must log in to create a %s' % kind)
        return HttpResponseRedirect('%s?next=%s' % (reverse('users.views.login'), request.path))
    c = {}
    if parent:
        if kind != 'proof':
            raise Http404
        c['parent'] = get_object_or_404(FinalItem, final_id=parent, itemtype='T')
    if request.method == 'GET':
        form = EditItemForm()
    else:
        form = EditItemForm(request.POST)
        is_valid = form.is_valid()
        primarytags   = form.pre_validate['primarytags']
        secondarytags = form.pre_validate['secondarytags']
        body          = form.pre_validate['body']
        if request.POST['submit'].lower() == 'preview':
            c['preview'] = { 'kind':          kind,
                             'body':          body,
                             'parent':        c.get('parent'),
                             'primarytags':   primarytags,
                             'secondarytags': secondarytags }
        elif is_valid:                 # save draft
            item = DraftItem.objects.add_item(request.user, kind, body,
                                              primarytags, secondarytags,
                                              c.get('parent'))
            message = u'%s successfully created' % item
            logger.debug(message)
            messages.success(request, message)
            return HttpResponseRedirect(reverse('items.views.show', args=[item.id]))
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
    item = get_object_or_404(DraftItem, pk=item_id)
    item_perms = get_user_item_permissions(request.user, item)
    if not item_perms['edit']:
        raise Http404
    if request.method == 'GET':
        form = EditItemForm({ 'body':          item.body,
                              'primarytags':   '\n'.join(item.primary_tags),
                              'secondarytags': '\n'.join(item.secondary_tags) })
    else:
        form = EditItemForm(request.POST)
        is_valid = form.is_valid()
        primarytags   = form.pre_validate['primarytags']
        secondarytags = form.pre_validate['secondarytags']
        body          = form.pre_validate['body']
        if request.POST['submit'].lower() == 'preview':
            c['preview'] = { 'id':            item.id,
                             'kind':          item.get_itemtype_display(),
                             'body':          body,
                             'parent':        item.parent,
                             'primarytags':   primarytags,
                             'secondarytags': secondarytags }
        elif is_valid:                 # update draft
            DraftItem.objects.update_item(item, request.user, body,
                                          primarytags, secondarytags)
            message = u'%s successfully updated' % item
            logger.debug(message)
            messages.success(request, message)
            return HttpResponseRedirect(reverse('items.views.show', args=[item_id]))
    c.update(dict(item=item, form=form))
    if item.itemtype == 'D':
        c['primary_text'] = 'Terms defined'
    elif item.itemtype == 'T':
        c['primary_text'] = 'Name(s) of theorem'
    return render(request, 'items/edit.html', c)

@require_GET
def show(request, item_id):
    item = get_object_or_404(DraftItem, pk=item_id)
    permissions = get_user_item_permissions(request.user, item)
    if not permissions['view']:
        raise Http404 
    c = { 'item': item,
          'perm': permissions }
    return render(request, 'items/show.html', c)

@require_GET
def show_final(request, final_id):
    item = get_object_or_404(FinalItem, final_id=final_id)
    validation_count = item.sourcevalidation_set.count()
    proof_count = item.finalitem_set.filter(itemtype='P', status='F').count() if item.itemtype == 'T' else 0
    c = { 'item':             item,
          'perm':             get_user_item_permissions(request.user, item),
          'validation_count': validation_count,
          'proof_count':      proof_count }
    if validation_count and 'vals' in request.GET:
        c['validation_list'] = item.sourcevalidation_set.all()
    if proof_count and 'prfs' in request.GET:
        c['proof_list'] = item.finalitem_set.filter(itemtype='P', status='F').all()
    return render(request, 'items/show_final.html', c)

@require_POST
def change_status(request):
    if not request.user.is_authenticated():
        raise Http404
    item_id = request.POST['item']
    item = get_object_or_404(DraftItem, pk=item_id)
    own_item = request.user == item.created_by
    if request.POST['status'] == 'publish':
        if not own_item or item.status not in ['D', 'R']:
            raise Http404
        fitem = FinalItem.objects.add_item(item)
        add_final_item_dependencies(fitem)
        item.delete()
        return HttpResponseRedirect(reverse('items.views.show_final', args=[fitem.final_id]))
    else:   # to review
        if not own_item or item.status != 'D':
            raise Http404 
        item.make_review()
        return HttpResponseRedirect(reverse('items.views.show', args=[item.id]))

@require_POST
def delete_public(request):
    if not (request.user.is_authenticated() and request.user.is_admin):
        raise Http404
    item_id = request.POST['item']
    item = get_object_or_404(FinalItem, pk=item_id)
    item.delete()
    return HttpResponseRedirect(reverse('main.views.index'))

@require_POST
def delete_draft(request):
    if not request.user.is_authenticated():
        raise Http404
    item_id = request.POST['item']
    item = get_object_or_404(DraftItem, pk=item_id)
    if request.user != item.created_by:
        raise Http404
    item.delete()
    return HttpResponseRedirect(reverse('users.views.profile', args=[request.user.get_username()]))
