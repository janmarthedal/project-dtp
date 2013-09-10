from django.shortcuts import render
from django.views.decorators.http import require_safe
from sources.models import RefNode
from main.helpers import init_context, logged_in_or_404

@require_safe
def index(request):
    c = init_context('sources')
    c['sourcelist'] = RefNode.objects.all()
    return render(request, 'sources/index.html', c)

@logged_in_or_404
@require_safe
def add_source(request):
    c = init_context('sources')
    return render(request, 'sources/add.html', c)
