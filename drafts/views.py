from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from drafts.models import DraftItem, ItemTypes

test_body = r"""The $n$th [harmonic number](=harmonic-number), $H_n$, is defined as

$$
H_n = 1 + \frac{1}{2} + \ldots + \frac{1}{n} = \sum_{k=1}^n \frac{1}{k}
$$

for $n \geq 1$."""

# view function helper
def new_item(request, item_type):
    item = DraftItem(creator=request.user, item_type=item_type, body='')
    context = {'title': 'New ' + item.get_item_type_display()}
    if request.method == 'POST':
        body = request.POST['src']
        item.body = body
        context['body'] = body
        if request.POST['submit'] == 'preview':
            html, defined, errors = item.prepare()
            context.update(item_html=html, defined=defined, errors=errors)
        elif request.POST['submit'] == 'save':
            item.save()
            return redirect(item)
    else:
        context['body'] = test_body
    return render(request, 'drafts/edit.html', context)

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
    context = {'title': 'New {} (Draft {})'.format(item.get_item_type_display(), item.id)}
    html, defined, errors = item.prepare()
    context.update(item_html=html, defined=defined, errors=errors)
    return render(request, 'drafts/show.html', context)
