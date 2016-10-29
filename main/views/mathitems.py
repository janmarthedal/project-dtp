import json
import re
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_safe, require_http_methods

from concepts.models import Concept
from equations.models import Equation
from main.item_helpers import get_refs_and_render
from mathitems.models import ItemTypes, MathItem
from validations.models import ItemValidation, Source

import logging
logger = logging.getLogger(__name__)

def decode_document(node, eqns):
    overrides = {}
    if 'concept' in node:
        overrides['concept'] = Concept.objects.get(id=node['concept']).name
    if 'eqn' in node:
        eqns.add(node['eqn'])
    if node.get('children'):
        overrides['children'] = [decode_document(child, eqns)
                                 for child in node['children']]
    return dict(node, **overrides) if overrides else node

def item_render(item):
    eqns = set()
    document = decode_document(json.loads(item.body), eqns)
    eqn_map = {equation.id: {'html': equation.html}
               for equation in Equation.objects.filter(id__in=eqns)}
    result = get_refs_and_render(item.item_type, document, eqn_map)
    if result['errors']:
        raise IllegalMathItem('Error in published item {}'.format(self.id))
    del result['errors']
    return result


@require_safe
def show_item(request, id_str):
    try:
        item = MathItem.objects.get_by_name(id_str)
    except MathItem.DoesNotExist:
        raise Http404('Item does not exist')
    item_data = item_render(item)
    context = {
        'title': str(item),
        'item': item,
        'item_data': item_data,
        'validations': item.itemvalidation_set.all()
    }
    if item.item_type == ItemTypes.THM:
        context['new_proof_link'] = reverse('new-prf', args=[item.get_name()])
        context['proofs'] = list(MathItem.objects.filter(item_type=ItemTypes.PRF, parent=item).order_by('id'))
    if item.item_type == ItemTypes.PRF:
        context['subtitle'] = 'of {}'.format(item.parent)
        context['parent_item'] = item.parent
        context['parent_item_data'] = item_render(item.parent)
    return render(request, 'mathitems/show.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def add_item_validation(request, id_str):
    try:
        item = MathItem.objects.get_by_name(id_str)
    except MathItem.DoesNotExist:
        raise Http404('Item does not exist')
    item_data = item_render(item)
    if request.method == 'POST':
        source = Source.objects.get(id=int(request.POST['source']))
        item_validation = ItemValidation.objects.create(created_by=request.user,
                                                        item=item,
                                                        source=source,
                                                        location=request.POST['location'])
        return HttpResponseRedirect(reverse('show-item', args=[id_str]))
    context = {
        'title': str(item),
        'item': item,
        'item_data': item_data,
        'types': Source.SOURCE_TYPE_CHOICES
    }
    if 'type' in request.GET:
        type_slug = request.GET['type']
        type_display = dict(Source.SOURCE_TYPE_CHOICES).get(type_slug)
        if type_display:
            context['type_slug'] = type_slug
            context['type_display'] = type_display
            if 'value' in request.GET:
                value = request.GET['value']
                try:
                    source, _ = Source.objects.get_or_create(source_type=type_slug, source_value=value)
                    context['source'] = source
                except ValidationError as ve:
                    context['error'] = '; '.join(ve.messages)
        else:
            context['error'] = 'Illegal validation type'
    return render(request, 'mathitems/add_item_validation.html', context)


# Helper
def item_home(request, item_type, new_draft_url=None):
    name = ItemTypes.NAMES[item_type]
    items = [{
        'item': item,
        'defines': list(Concept.objects.filter(conceptdefinition__item=item)
                            .order_by('name')
                            .values_list('name', flat=True))
    } for item in MathItem.objects.filter(item_type=item_type).order_by('-created_at')]
    context = {
        'title': name,
        'items': items,
    }
    if new_draft_url:
        context.update(new_name='New ' + name, new_url=new_draft_url)
    return render(request, 'mathitems/item-home.html', context)


@require_safe
def def_home(request):
    return item_home(request, ItemTypes.DEF, reverse('new-def'))


@require_safe
def thm_home(request):
    return item_home(request, ItemTypes.THM, reverse('new-thm'))


@require_safe
def prf_home(request):
    return item_home(request, ItemTypes.PRF)
