from django.contrib import messages
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods, require_safe
from main.models import DraftItem, MathItem

@require_http_methods(['GET', 'POST'])
def create_item(request, type_name):
    try:
        item_type = {long: short for short, long in MathItem.MATH_ITEM_TYPES}[type_name]
    except KeyError:
        raise Http404
    if request.method == 'POST':
        body = request.POST['body']
        item = DraftItem(item_type=item_type, body=body)
        item.save()
        messages.success(request, '{} successfully created'.format(item.get_title()))
        return redirect(item)
    return render(request, 'main/create.html', {'typename': type_name})

@require_safe
def home(request):
    return render(request, 'main/home.html')

@require_safe
def drafts_home(request):
    items = DraftItem.objects.order_by('id')
    return render(request, 'main/drafts-home.html', {'items': items})

@require_safe
def view_draft(request, slug):
    try:
        item = DraftItem.objects.get(id=int(slug))
    except DraftItem.DoesNotExist:
        raise Http404
    return render(request, 'main/view-draft.html', {'item': item})
