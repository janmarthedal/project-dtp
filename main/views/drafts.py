import json
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_safe, require_http_methods

from concepts.models import Concept
from drafts.models import DraftItem
from equations.models import get_equation_html, publish_equations
from main.elasticsearch import index_item
from main.item_helpers import get_refs_and_render, create_item_meta_data, item_to_markup, create_concept_meta
from mathitems.models import ItemTypes, MathItem
from permissions.manager import has_perm
from project.server_com import convert_markup

#import logging
#logger = logging.getLogger(__name__)


def draft_prepare(draft):
    body = draft.body.strip()
    document, eqns, concepts = convert_markup(body)
    rendered_eqns = get_equation_html(eqns)
    return document, rendered_eqns, concepts


def save_concepts(concepts):
    concept_conversions = {}
    for id, name in concepts.items():
        concept = Concept.objects.get_or_create(name=name)[0]
        concept_conversions[int(id)] = concept.id
    return concept_conversions


def convert_document(node, eqn_conv, concept_conv):
    overrides = {}
    if 'concept' in node:
        overrides['concept'] = concept_conv[node['concept']]
    if 'eqn' in node:
        overrides['eqn'] = eqn_conv[node['eqn']]
    if node.get('children'):
        overrides['children'] = [convert_document(child, eqn_conv, concept_conv)
                                 for child in node['children']]
    if overrides:
        return dict(node, **overrides)
    return node


def publish(user, item_type, parent, document, eqns, concepts):
    eqn_conversions = publish_equations(eqns)
    concept_conversions = save_concepts(concepts)
    document = convert_document(document, eqn_conversions, concept_conversions)
    item = MathItem(created_by=user, item_type=item_type, body=json.dumps(document))
    if parent:
        item.parent = parent
    item.save()
    concept_ids = create_item_meta_data(item)
    for concept_id in concept_ids:
        create_concept_meta(concept_id)
    index_item(item)
    return item


def edit_item(request, item):
    context = {'title': '{} {}'.format('Edit' if item.id else 'New', item)}
    if request.method == 'POST':
        item.body = request.POST['src']
        if request.POST['submit'] == 'preview':
            document, eqns, concepts = draft_prepare(item)
            item_data = get_refs_and_render(item.item_type, document, eqns, concepts)
            context['item_data'] = item_data
        elif request.POST['submit'] == 'save':
            item.save()
            return redirect(item)
    context['item'] = item
    context['can_save'] = has_perm('draft', request.user)
    return render(request, 'drafts/edit.html', context)


def new_item(request, item_type, parent=None):
    item = DraftItem(created_by=request.user, item_type=item_type, body='')
    if parent:
        item.parent = parent
    return edit_item(request, item)


@login_required
@require_http_methods(['HEAD', 'GET', 'POST'])
def new_definition(request):
    return new_item(request, ItemTypes.DEF)


@login_required
@require_http_methods(['HEAD', 'GET', 'POST'])
def new_theorem(request):
    return new_item(request, ItemTypes.THM)


@login_required
@require_http_methods(['HEAD', 'GET', 'POST'])
def new_proof(request, thm_id_str):
    parent = MathItem.objects.get_by_name(thm_id_str)
    return new_item(request, ItemTypes.PRF, parent)


@login_required
@require_http_methods(['HEAD', 'GET', 'POST'])
def show_draft(request, id_str):
    item = get_object_or_404(DraftItem, id=int(id_str), created_by=request.user)
    document, eqns, concepts = draft_prepare(item)
    if request.method == 'POST':
        if request.POST['submit'] == 'delete':
            item.delete()
            return redirect('list-drafts')
        elif request.POST['submit'] == 'publish':
            mathitem = publish(request.user, item.item_type, item.parent, document, eqns, concepts)
            item.delete()
            return redirect(mathitem)
    return render(request, 'drafts/show.html', {
        'title': str(item),
        'item': item,
        'item_data': get_refs_and_render(item.item_type, document, eqns, concepts),
        'can_publish': has_perm('publish', request.user)
    })


@login_required
@require_http_methods(['HEAD', 'GET', 'POST'])
def edit_draft(request, id_str):
    item = get_object_or_404(DraftItem, id=int(id_str), created_by=request.user)
    return edit_item(request, item)


@login_required
@require_safe
def list_drafts(request):
    return render(request, 'drafts/list.html', {
        'title': 'My Drafts',
        'items': DraftItem.objects.filter(created_by=request.user).order_by('-updated_at'),
    })


@login_required
def copy_to_draft(request, id_str):
    try:
        item = MathItem.objects.get_by_name(id_str)
    except MathItem.DoesNotExist:
        return HttpResponseBadRequest()
    markup = item_to_markup(item)
    draft = DraftItem(created_by=request.user, item_type=item.item_type, body=markup)
    if item.parent:
        draft.parent = item.parent
    draft.save()
    return HttpResponseRedirect(reverse('show-draft', args=[draft.id]))
