from django.http import HttpResponseRedirect, Http404
from django.views.decorators.http import require_GET
from django.shortcuts import render
from items.models import FinalItem

@require_GET
def index(request):
    if not (request.user.is_authenticated() and request.user.is_admin):
        raise Http404
    return render(request, 'admin/index.html')

@require_GET
def recalc_deps(request):
    if not (request.user.is_authenticated() and request.user.is_admin):
        raise Http404
    fitems = FinalItem.objects.filter(status='F').all()
    for fitem in fitems:
        fitem.set_dependencies()
    c = { 'final_item_count': len(fitems) }
    return render(request, 'admin/recalc_deps.html', c)

