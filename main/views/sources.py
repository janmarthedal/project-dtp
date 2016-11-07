from django.shortcuts import render
from django.views.decorators.http import require_safe

from validations.models import Source


@require_safe
def sources_list(request):
    return render(request, 'sources/list.html', {
        'title': 'Sources',
        'sources': Source.objects.all(),
    })
