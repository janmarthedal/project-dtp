from django.http import Http404
from django.views.decorators.http import require_GET
from django.shortcuts import render
from analysis.models import rebuild_dependencies, build_concept_definitions

@require_GET
def index(request):
    if not (request.user.is_authenticated() and request.user.is_admin):
        raise Http404
    return render(request, 'admin/index.html')

@require_GET
def recalc_deps(request):
    if not (request.user.is_authenticated() and request.user.is_admin):
        raise Http404
    c = rebuild_dependencies()
    return render(request, 'admin/recalc_deps.html', c)

@require_GET
def build_concept_defs(request):
    if not (request.user.is_authenticated() and request.user.is_admin):
        raise Http404
    c = build_concept_definitions()
    return render(request, 'admin/build_concept_defs.html', c)

