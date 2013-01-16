from django.shortcuts import render
from django.views.decorators.http import require_safe
from main.helpers import init_context

@require_safe
def index(request):
    c = init_context(request)
    return render(request, 'index.html', c)

