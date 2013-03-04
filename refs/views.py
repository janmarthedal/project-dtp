from django.shortcuts import render
from django.views.decorators.http import require_safe
from refs.models import RefNode

@require_safe
def index(request):
    all_sources = RefNode.objects.all()
    return render(request, 'refs/index.html', { 'sourcelist': all_sources })
