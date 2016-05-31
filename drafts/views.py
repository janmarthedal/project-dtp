from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from drafts.models import DraftItem, ItemTypes

test_body = r"""The $n$th [harmonic number](=harmonic-number), $H_n$, is defined as

$$
H_n = 1 + \frac{1}{2} + \ldots + \frac{1}{n} = \sum_{k=1}^n \frac{1}{k}
$$

for $n \geq 1$."""

def edit_item(request, item):
    context = {'title': '{} {}'.format('Edit' if item.id else 'New', item)}
    if request.method == 'POST':
        item.body = request.POST['src']
        if request.POST['submit'] == 'preview':
            context['item_data'] = item.prepare()
        elif request.POST['submit'] == 'save':
            item.save()
            return redirect(item)
    context['item'] = item
    return render(request, 'drafts/edit.html', context)

def new_item(request, item_type):
    item = DraftItem(creator=request.user, item_type=item_type, body=test_body)
    return edit_item(request, item)

@login_required
def new_definition(request):
    return new_item(request, ItemTypes.DEF)

@login_required
def new_theorem(request):
    return new_item(request, ItemTypes.THM)

@login_required
def show_draft(request, id_str):
    item = get_object_or_404(DraftItem, id=int(id_str))
    if item.creator != request.user:
        return HttpResponseForbidden()
    context = {
        'title': str(item),
        'item': item,
        'item_data': item.prepare()
    }
    return render(request, 'drafts/show.html', context)

@login_required
def edit_draft(request, id_str):
    item = get_object_or_404(DraftItem, id=int(id_str))
    if item.creator != request.user:
        return HttpResponseForbidden()
    return edit_item(request, item)

@login_required
def list_drafts(request):
    context = {
        'title': 'My Drafts',
        'items': DraftItem.objects.filter(creator=request.user).order_by('id'),
    }
    return render(request, 'drafts/list.html', context)
