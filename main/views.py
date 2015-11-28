from django.http import Http404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods, require_GET
from main.models import MathItem

@require_http_methods(['GET', 'POST'])
def create_item(request, item_type):
    if item_type not in ['definition', 'theorem', 'proof']:
        raise Http404
    if request.method == 'POST':
        body = request.POST['body']
        item = MathItem(item_type=item_type[0].upper(), body=body)
        item.save()
        return redirect(item)
    return render(request, 'main/create.html', {'itemtype': item_type})

@require_GET
def view_item(request, slug):
    try:
        item = MathItem.objects.get(id=int(slug[1:]), item_type=slug[0])
    except MathItem.DoesNotExist:
        raise Http404
    return render(request, 'main/view-item.html', {'item': item})
