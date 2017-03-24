import json
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.views.decorators.http import require_safe, require_http_methods

from concepts.models import Concept
from equations.models import Equation
from keywords.models import Keyword, ItemKeyword
from main.item_helpers import get_refs_and_render, item_to_markup
from main.views.helpers import prepare_item_view_list
from mathitems.models import ItemTypes, MathItem, IllegalMathItem
from permissions.manager import has_perm
from validations.models import ItemValidation, Source

#import logging
#logger = logging.getLogger(__name__)

def decode_document(node, eqn_set, concept_set):
    if 'concept' in node:
        concept_set.add(node['concept'])
    if 'eqn' in node:
        eqn_set.add(node['eqn'])
    if node.get('children'):
        children = [decode_document(child, eqn_set, concept_set)
                    for child in node['children']]
        return dict(node, children=children)
    return node

def item_render(item):
    eqn_set = set()
    concept_set = set()
    document = decode_document(json.loads(item.body), eqn_set, concept_set)
    eqn_map = {eqn.id: {'html': eqn.html}
               for eqn in Equation.objects.filter(id__in=eqn_set)}
    concept_map = {concept.id: concept.name
                   for concept in Concept.objects.filter(id__in=concept_set)}
    result = get_refs_and_render(item.item_type, document, eqn_map, concept_map)
    if result['errors']:
        raise IllegalMathItem('Error in published item {}: {}'.format(item.id, result['error']))
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
        'keywords': Keyword.objects.filter(itemkeyword__item=item).order_by('name').all(),
        'validations': item.itemvalidation_set.all(),
        'can_add_validation': has_perm('validation', request.user),
        'can_edit_keywords': has_perm('keyword', request.user),
    }
    if item.item_type == ItemTypes.THM:
        context['can_add_proof'] = True
        context['proofs'] = list(MathItem.objects.filter(item_type=ItemTypes.PRF, parent=item).order_by('id'))
    if item.item_type == ItemTypes.PRF:
        context['subtitle'] = 'of {}'.format(item.parent)
        context['parent_item'] = item.parent
        context['parent_item_data'] = item_render(item.parent)
    return render(request, 'mathitems/show.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def edit_item_keywords(request, id_str):
    try:
        item = MathItem.objects.get_by_name(id_str)
    except MathItem.DoesNotExist:
        raise Http404('Item does not exist')
    if not has_perm('keyword', request.user):
        raise PermissionDenied('User not allowed to edit keywords')
    if request.method == 'POST':
        if 'delete' in request.POST:
            itemkw = ItemKeyword.objects.get(pk=int(request.POST['delete']))
            itemkw.delete()
            if ItemKeyword.objects.filter(keyword=itemkw.keyword).count() == 0:
                itemkw.keyword.delete()
        else:
            if request.POST['kw']:
                keyword, _ = Keyword.objects.get_or_create(name=request.POST['kw'])
                itemkw, _ = ItemKeyword.objects.get_or_create(
                                item=item, keyword=keyword, defaults={'created_by': request.user})
    item_data = item_render(item)
    context = {
        'title': str(item),
        'item': item,
        'item_data': item_data,
        'itemkeywords': ItemKeyword.objects.filter(item=item).order_by('keyword__name').all(),
    }
    if item.item_type == ItemTypes.PRF:
        context['subtitle'] = 'of {}'.format(item.parent)
        context['parent_item'] = item.parent
        context['parent_item_data'] = item_render(item.parent)
    return render(request, 'mathitems/edit-item-keywords.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def add_item_validation(request, id_str):
    try:
        item = MathItem.objects.get_by_name(id_str)
    except MathItem.DoesNotExist:
        raise Http404('Item does not exist')
    if not has_perm('validation', request.user):
        raise PermissionDenied('User not allowed to add validation')
    item_data = item_render(item)
    if request.method == 'POST':
        source = Source.objects.get(id=int(request.POST['source']))
        ItemValidation.objects.create(created_by=request.user,
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
    return render(request, 'mathitems/add-item-validation.html', context)


@require_safe
def def_home(request):
    items = MathItem.objects.filter(item_type=ItemTypes.DEF).order_by('-created_at')
    return render(request, 'mathitems/definitions-home.html', {
        'title': 'Definitions',
        'latest': prepare_item_view_list(items[:5]),
        'no_vals': prepare_item_view_list(items.annotate(vals=Count('itemvalidation')).filter(vals=0)[:5]),
        'no_defs': Concept.objects.filter(conceptmeta__def_count=0, conceptmeta__ref_count__gt=0).order_by('-conceptmeta__ref_count', 'name'),
    })


@require_safe
def thm_home(request):
    items = MathItem.objects.filter(item_type=ItemTypes.THM).order_by('-created_at')
    return render(request, 'mathitems/theorems-home.html', {
        'title': 'Theorems',
        'latest': prepare_item_view_list(items[:5]),
        'without_proof': prepare_item_view_list(items.annotate(proofs=Count('mathitem')).filter(proofs=0)[:5]),
        'no_vals': prepare_item_view_list(items.annotate(vals=Count('itemvalidation')).filter(vals=0)[:5]),
    })


@require_safe
def prf_home(request):
    items = MathItem.objects.filter(item_type=ItemTypes.PRF).order_by('-created_at')
    return render(request, 'mathitems/proofs-home.html', {
        'title': 'Proofs',
        'latest': prepare_item_view_list(items[:5]),
        'no_vals': prepare_item_view_list(items.annotate(vals=Count('itemvalidation')).filter(vals=0)[:5]),
    })


@require_safe
def dump_item(request, id_str):
    try:
        item = MathItem.objects.get_by_name(id_str)
    except MathItem.DoesNotExist:
        raise Http404('Item does not exist')
    markup = item_to_markup(item)
    return render(request, 'mathitems/dump.txt', {
        'item': item,
        'markup': markup,
        'validations': item.itemvalidation_set.all()
    }, content_type="text/plain")
