import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_safe, require_http_methods

from equations.models import get_equation_html, freeze_equations
from drafts.models import DraftItem, ItemTypes
from main.item_helpers import get_refs_and_render
from mathitems.models import Concept, ConceptDefinition, MathItem
from project.server_com import convert_markup, render_item, render_eqns

import logging
logger = logging.getLogger(__name__)


def draft_prepare(draft):
    body = draft.body.strip()
    document, eqns = convert_markup(body)
    rendered_eqns = get_equation_html(eqns)
    return document, rendered_eqns


def encode_document(node, eqn_map, defines):
    overrides = {}
    if 'concept' in node:
        concept = Concept.objects.get_or_create(name=node['concept'])[0]
        overrides['concept'] = concept.id
        if node.get('type') == 'concept-def':
            defines[concept.id] = concept
    if 'eqn' in node:
        overrides['eqn'] = eqn_map[node['eqn']]
    if node.get('children'):
        overrides['children'] = [encode_document(child, eqn_map, defines)
                                 for child in node['children']]
    return dict(node, **overrides) if overrides else node


def publish(user, item_type, parent, document, eqns):
    eqn_conversions = freeze_equations(eqns)
    defines = {}
    document = encode_document(document, eqn_conversions, defines)
    item = MathItem(created_by=user, item_type=item_type, body=json.dumps(document))
    if parent:
        item.parent = parent
    item.save()
    if item_type == ItemTypes.DEF:
        ConceptDefinition.objects.bulk_create(
            ConceptDefinition(item=item, concept=concept) for concept in defines.values())
    return item


def edit_item(request, item):
    context = {'title': '{} {}'.format('Edit' if item.id else 'New', item)}
    if request.method == 'POST':
        item.body = request.POST['src']
        if request.POST['submit'] == 'preview':
            document, eqns = draft_prepare(item)
            item_data = get_refs_and_render(item.item_type, document, eqns)
            context['item_data'] = item_data
        elif request.POST['submit'] == 'save':
            item.save()
            return redirect(item)
    context['item'] = item
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
    document, eqns = draft_prepare(item)
    if request.method == 'POST':
        if request.POST['submit'] == 'delete':
            item.delete()
            return redirect('list-drafts')
        elif request.POST['submit'] == 'publish':
            mathitem = publish(request.user, item.item_type, item.parent, document, eqns)
            item.delete()
            return redirect(mathitem)
    return render(request, 'drafts/show.html', {
        'title': str(item),
        'item': item,
        'item_data': get_refs_and_render(item.item_type, document, eqns),
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
