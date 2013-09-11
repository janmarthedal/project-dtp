from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_safe, require_http_methods
from items.models import FinalItem
from main.helpers import init_context, logged_in_or_404
from sources.models import RefNode, SourceValidation

@require_safe
def index(request):
    c = init_context('sources', sourcelist=RefNode.objects.all())
    return render(request, 'sources/index.html', c)

@logged_in_or_404
@require_safe
def add_source(request):
    c = init_context('sources', mode='simple')
    return render(request, 'sources/add.html', c)

@logged_in_or_404
@require_safe
def add_source_for_item(request, item_id):
    item = get_object_or_404(FinalItem, final_id=item_id)
    c = init_context('sources', mode='item', item=item)
    return render(request, 'sources/add.html', c)

@logged_in_or_404
@require_http_methods(['GET', 'POST'])
def add_location_for_item(request, item_id, source_id):
    item = get_object_or_404(FinalItem, final_id=item_id)
    source = get_object_or_404(RefNode, pk=source_id)
    if request.method == 'GET':
        c = init_context('sources', item=item, source=source)
        return render(request, 'sources/add_location_for_item.html', c)
    else:
        location = request.POST['location'].strip() or None
        SourceValidation.objects.create(created_by=request.user,
                                        item=item,
                                        source=source,
                                        location=location)
        return HttpResponseRedirect(reverse('items.views.show_final', args=[item.final_id]))
