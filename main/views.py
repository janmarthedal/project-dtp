from django.shortcuts import render
from main.models import Item, ItemTag, Tag
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_safe
from main.helpers import init_context

@require_safe
def index(request):
    c = init_context(request)
    return render(request, 'index.html', c)

