from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.views.decorators.http import require_safe
from main.helpers import init_context
from tags.models import Category

import logging
logger = logging.getLogger(__name__)

def category_link_from_tags(tags):
    return reverse('tags.views.show', args=['/'.join(tags)])

@require_safe
def show(request, path):
    c = init_context('categories')

    if path:
        tags = path.split('/')
        category_items = [dict(name = tags[i], link = category_link_from_tags(tags[0:i])) for i in range(0, len(tags))]
    else:
        tags = []
        category_items = [dict(name = None, link = category_link_from_tags([]))]
    
    category = Category.objects.from_tag_names_or_404(tags)
    listing = Category.objects.filter(parent=category).order_by('tag__name').values_list('tag__name', flat=True)
    result_list = [dict(name = name, link = category_link_from_tags(tags + [name])) for name in listing]
    
    c.update(category_items = category_items, result_list = result_list)
    return render(request, 'tags/index.html', c)
