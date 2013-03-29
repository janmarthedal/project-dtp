from django.http import Http404
from django.views.decorators.http import require_GET
from django.shortcuts import render
from analysis.models import rebuild_dependencies, build_concept_definitions
from main.helpers import init_context


@require_GET
def index(request):
    c = init_context('admin')
    if not (request.user.is_authenticated() and request.user.is_admin):
        raise Http404
    return render(request, 'admin/index.html', c)

@require_GET
def recalc_deps(request):
    c = init_context('admin')
    if not (request.user.is_authenticated() and request.user.is_admin):
        raise Http404
    c.update(rebuild_dependencies())
    return render(request, 'admin/recalc_deps.html', c)

@require_GET
def build_concept_defs(request):
    c = init_context('admin')
    if not (request.user.is_authenticated() and request.user.is_admin):
        raise Http404
    c.update(build_concept_definitions())
    return render(request, 'admin/build_concept_defs.html', c)
