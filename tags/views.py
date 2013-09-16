from django.shortcuts import render
from django.views.decorators.http import require_safe
from main.helpers import init_context

import logging
logger = logging.getLogger(__name__)

@require_safe
def show(request, path):
    c = init_context('categories')
    logger.info(path)
    return render(request, 'tags/index.html', c)
