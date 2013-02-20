from django.http import Http404
from django.views.decorators.http import require_GET
from django.shortcuts import render
from analysis.models import recalc_all

@require_GET
def index(request):
    if not (request.user.is_authenticated() and request.user.is_admin):
        raise Http404
    return render(request, 'admin/index.html')

@require_GET
def recalc_deps(request):
    if not (request.user.is_authenticated() and request.user.is_admin):
        raise Http404
    c = recalc_all()
    return render(request, 'admin/recalc_deps.html', c)
