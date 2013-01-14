from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from main.helpers import init_context

def new_item(request, kind):
    c = init_context(request)
    c['kind'] = kind
    return render(request, 'items/edit.html', c)

@login_required
def new_theorem(request):
    return new_item(request, 'theorem')

@login_required
def new_definition(request):
    return new_item(request, 'definition')

@login_required
@require_POST
def edit(request):
    c = init_context(request)
    c['kind']        = request.POST['kind']
    c['body']        = request.POST['body']
    c['primarytags'] = request.POST['primarytags']
    c['othertags']   = request.POST['othertags']
    return render(request, 'items/edit.html', c)

