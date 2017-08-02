import json
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_safe, require_http_methods

from concepts.models import Concept
from equations.models import RenderedEquation
from keywords.models import Keyword, ItemKeyword
from main.elasticsearch import index_item, item_search
from main.item_helpers import get_refs_and_render, item_to_markup
from main.views.helpers import prepare_item_view_list, LIST_PAGE_SIZE
from mathitems.models import ItemTypes, MathItem, IllegalMathItem
from project.paginator import QuerySetPaginator, Paginator, PaginatorError
from validations.models import ItemValidation, Source
from userdata.permissions import has_perm, require_perm

# import logging
# logger = logging.getLogger(__name__)


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
    eqn_map = {reqn.pk: {'html': reqn.html}
               for reqn in RenderedEquation.objects.filter(pk__in=eqn_set)}
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
        'kw_edit_link': has_perm('keyword', request.user) and reverse('edit-item-keywords', args=[item.get_name()]),
    }
    if item.item_type == ItemTypes.THM:
        context['can_add_proof'] = True
        context['proofs'] = list(MathItem.objects.filter(item_type=ItemTypes.PRF, parent=item).order_by('id'))
    if item.item_type == ItemTypes.PRF:
        context['subtitle'] = 'of {}'.format(item.parent)
        context['parent_item'] = item.parent
        context['parent_item_data'] = item_render(item.parent)
    return render(request, 'mathitems/show.html', context)


@require_http_methods(['GET', 'POST'])
@login_required
@require_perm('keyword')
def edit_item_keywords(request, id_str):
    try:
        item = MathItem.objects.get_by_name(id_str)
    except MathItem.DoesNotExist:
        raise Http404('Item does not exist')
    if request.method == 'POST':
        if 'delete' in request.POST:
            itemkw = ItemKeyword.objects.get(pk=int(request.POST['delete']))
            itemkw.delete()
        else:
            if request.POST['kw']:
                keyword, _ = Keyword.objects.get_or_create(name=request.POST['kw'])
                itemkw, _ = ItemKeyword.objects.get_or_create(
                                item=item, keyword=keyword, defaults={'created_by': request.user})
        index_item(item)
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


@require_http_methods(['GET', 'POST'])
@login_required
@require_perm('validation')
def add_item_validation(request, id_str):
    try:
        item = MathItem.objects.get_by_name(id_str)
    except MathItem.DoesNotExist:
        raise Http404('Item does not exist')
    item_data = item_render(item)
    if request.method == 'POST':
        source = Source.objects.get(id=int(request.POST['source']))
        ItemValidation.objects.create(created_by=request.user,
                                      item=item,
                                      source=source,
                                      location=request.POST['location'])
        return redirect('show-item', id_str)
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


def get_latest_mathitems(item_type):
    return MathItem.objects.filter(item_type=item_type).order_by('-created_at')


def get_first_elements_check_more(query, count):
    items = query[:(count+1)]
    return items[:count], len(items) > count


@require_safe
def def_home(request):
    items = get_latest_mathitems(ItemTypes.DEF)
    latest, more_latest = get_first_elements_check_more(items, 5)
    return render(request, 'mathitems/definitions-home.html', {
        'title': 'Definitions',
        'latest': prepare_item_view_list(latest),
        'latest_all': more_latest and reverse('def-list'),
        'no_vals': prepare_item_view_list(items.annotate(vals=Count('itemvalidation')).filter(vals=0)[:5]),
        'no_defs': Concept.objects.filter(conceptmeta__def_count=0, conceptmeta__ref_count__gt=0).order_by('-conceptmeta__ref_count', 'name'),
    })


@require_safe
def thm_home(request):
    items = get_latest_mathitems(ItemTypes.THM)
    latest, more_latest = get_first_elements_check_more(items, 5)
    return render(request, 'mathitems/theorems-home.html', {
        'title': 'Theorems',
        'latest': prepare_item_view_list(latest),
        'latest_all': more_latest and reverse('thm-list'),
        'without_proof': prepare_item_view_list(items.annotate(proofs=Count('mathitem')).filter(proofs=0)[:5]),
        'no_vals': prepare_item_view_list(items.annotate(vals=Count('itemvalidation')).filter(vals=0)[:5]),
    })


@require_safe
def prf_home(request):
    items = get_latest_mathitems(ItemTypes.PRF)
    latest, more_latest = get_first_elements_check_more(items, 5)
    return render(request, 'mathitems/proofs-home.html', {
        'title': 'Proofs',
        'latest': prepare_item_view_list(latest),
        'latest_all': more_latest and reverse('prf-list'),
        'no_vals': prepare_item_view_list(items.annotate(vals=Count('itemvalidation')).filter(vals=0)[:5]),
    })


def item_list_page(request, title, query):
    try:
        paginator = QuerySetPaginator(request, query, LIST_PAGE_SIZE)
    except PaginatorError as pe:
        return redirect(pe.url)

    return render(request, 'mathitems/item-list-page.html', {
        'title': title,
        'items': prepare_item_view_list(paginator.get_items()),
        'paginator': paginator
    })


@require_safe
def def_list(request):
    return item_list_page(request, 'Latest Definitions', get_latest_mathitems(ItemTypes.DEF))


@require_safe
def thm_list(request):
    return item_list_page(request, 'Latest Theorems', get_latest_mathitems(ItemTypes.THM))


@require_safe
def prf_list(request):
    return item_list_page(request, 'Latest Proofs', get_latest_mathitems(ItemTypes.PRF))


def item_search_helper(request, type_name):
    query = request.GET['q']
    try:
        paginator = Paginator(request, LIST_PAGE_SIZE)
        results, total = item_search(query, type_name, paginator.per_page * (paginator.page - 1), paginator.per_page)
        paginator.set_count(total)
    except PaginatorError as pe:
        return redirect(pe.url)

    name = type_name.capitalize()
    return render(request, 'mathitems/item-search-page.html', {
        'title': '{} Search'.format(name),
        'query': query,
        'items': prepare_item_view_list(MathItem.objects.get_by_name(name) for name in results),
        'paginator': paginator
    })


@require_safe
def def_search(request):
    return item_search_helper(request, 'definition')


@require_safe
def thm_search(request):
    return item_search_helper(request, 'theorem')


@require_safe
def prf_search(request):
    return item_search_helper(request, 'proof')


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
