from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from main.helpers import init_context

@login_required
def new(request, kind):
    c = init_context(request)
    c['kind'] = kind
    if request.method == 'POST':
        c['body']        = request.POST['body']
        c['primarytags'] = request.POST['primarytags']
        c['othertags']   = request.POST['othertags']
    return render(request, 'items/new.html', c)

