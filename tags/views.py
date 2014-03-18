from urllib.parse import unquote
from django.core.urlresolvers import reverse
from django.shortcuts import render, Http404
from django.views.decorators.http import require_safe
from items.helpers import request_to_search_data
from items.models import FinalItem
from items.views import render_search
from main.helpers import init_context
from tags.models import Category

import logging
logger = logging.getLogger(__name__)

def category_link_from_tags(tags):
    return reverse('tags.views.browse', args=['/'.join(tags)])

def path_to_category_items(path):
    tags = path.split('/') if path else []
    return [{'name': tags[i], 'link': category_link_from_tags(tags[0:i])} for i in range(0, len(tags))]

@require_safe
def browse(request, path):
    category_items = path_to_category_items(path)
    tags = path.split('/') if path else []
    category = Category.objects.from_tag_names_or_404(tags)
    listing = Category.objects.filter(parent=category).order_by('tag__name').values_list('tag__name', flat=True)
    result_list = [{'name': name, 'link': category_link_from_tags(tags + [name])} for name in listing]
    definition_count = FinalItem.objects.filter(status='F', itemtype='D', finalitemcategory__primary=True,
                                                finalitemcategory__category=category).count()
    theorem_count = FinalItem.objects.filter(status='F', itemtype='T', finalitemcategory__primary=True,
                                                finalitemcategory__category=category).count()
    c = init_context('categories', category_items=category_items, result_list=result_list,
                     path=path, def_count=definition_count, thm_count=theorem_count)
    return render(request, 'tags/browse.html', c)

def _finals_in_category(request, path, itemtype):
    if not path:
        raise Http404
    tags = map(unquote, path.split('/'))
    category = Category.objects.from_tag_names_or_404(tags)
    search_data = request_to_search_data(request)
    search_data['type'] = itemtype
    search_data['pricat'] = category.pk
    return render_search(request, search_data)

@require_safe
def definitions_in_category(request, path):
    return _finals_in_category(request, path, 'D')

@require_safe
def theorems_in_category(request, path):
    return _finals_in_category(request, path, 'T')
