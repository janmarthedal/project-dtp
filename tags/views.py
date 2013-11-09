import urllib
from django.core.urlresolvers import reverse
from django.shortcuts import render, Http404
from django.views.decorators.http import require_safe
from items.helpers import item_search_to_json
from main.helpers import init_context
from tags.models import Category

import logging
logger = logging.getLogger(__name__)

def category_link_from_tags(tags):
    return reverse('tags.views.browse', args=['/'.join(tags)])

@require_safe
def browse(request, path):
    tags = path.split('/') if path else []
    category_items = [dict(name = tags[i], link = category_link_from_tags(tags[0:i])) for i in range(0, len(tags))]
    category = Category.objects.from_tag_names_or_404(tags)
    listing = Category.objects.filter(parent=category).order_by('tag__name').values_list('tag__name', flat=True)
    result_list = [dict(name = name, link = category_link_from_tags(tags + [name])) for name in listing]
    c = init_context('categories', category_items = category_items, result_list = result_list, path = path)
    return render(request, 'tags/browse.html', c)

@require_safe
def list_definitions(request, path):
    if not path:
        raise Http404
    tags = map(urllib.unquote, path.split('/'))
    logger.debug(tags)
    category = Category.objects.from_tag_names_or_404(tags)
    c = init_context('definitions',
                     init_items = item_search_to_json(itemtype='D', category=category),
                     category = category.pk)
    return render(request, 'tags/list_definitions.html', c)
