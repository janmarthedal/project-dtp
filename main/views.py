from django.contrib import messages
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods, require_GET
from main.models import MathItem

@require_http_methods(['GET', 'POST'])
def create_item(request, type_name):
    item_type_map = {mit[1].lower(): mit[0] for mit in MathItem.MATH_ITEM_TYPES}
    try:
        item_type = item_type_map[type_name]
    except KeyError:
        raise Http404
    if request.method == 'POST':
        body = request.POST['body']
        item = MathItem(item_type=item_type, body=body)
        item.save()
        messages.success(request, '{} successfully created'.format(item.get_title()))
        return redirect(item)
    return render(request, 'main/create.html', {'typename': type_name})

@require_GET
def view_item(request, slug):
    try:
        item = MathItem.objects.get(id=int(slug[1:]), item_type=slug[0])
    except MathItem.DoesNotExist:
        raise Http404
    return render(request, 'main/view-item.html', {'item': item})
