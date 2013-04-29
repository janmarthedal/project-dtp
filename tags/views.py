from django.shortcuts import render
from django.views.decorators.http import require_safe
from main.helpers import init_context

@require_safe
def index(request):
    c = init_context('categories')
    return render(request, 'tags/index.html', c)
