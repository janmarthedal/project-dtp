from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_safe, require_http_methods

from mathitems.models import MathItem, ItemTypes
from validations.models import Source

import logging
logger = logging.getLogger(__name__)


class AddValidationForm(forms.Form):
    source_type = forms.ChoiceField(choices=Source.SOURCE_TYPE_CHOICES)
    source_value = forms.CharField(max_length=255)
    location = forms.CharField(max_length=255, required=False)


@require_safe
def show_item(request, id_str):
    item = MathItem.objects.get_by_name(id_str)
    item_data = item.render()
    context = {
        'title': str(item),
        'item': item,
        'item_data': item_data,
    }
    if item.item_type == ItemTypes.THM:
        context['new_proof_link'] = reverse('new-prf', args=[item.get_name()])
    return render(request, 'mathitems/show.html', context)


@require_http_methods(['GET', 'HEAD', 'POST'])
def add_item_validation(request, id_str):
    item = MathItem.objects.get_by_name(id_str)
    item_data = item.render()
    if request.method == 'POST':
        form = AddValidationForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('show-item', args=[id_str]))
    else:
        form = AddValidationForm()
    return render(request, 'mathitems/add_item_validation.html', {
        'title': str(item),
        'item': item,
        'item_data': item_data,
        'form': form
    })


# Helper
def item_home(request, item_type, new_draft_url=None):
    name = ItemTypes.NAMES[item_type]
    items = MathItem.objects.filter(item_type=item_type).order_by('-created_at')
    context = {
        'title': name,
        'items': items,
    }
    if new_draft_url:
        context.update(new_name='New ' + name, new_url=new_draft_url)
    return render(request, 'mathitems/item-home.html', context)


@require_safe
def def_home(request):
    return item_home(request, ItemTypes.DEF, reverse('new-def'))


@require_safe
def thm_home(request):
    return item_home(request, ItemTypes.THM, reverse('new-thm'))


@require_safe
def prf_home(request):
    return item_home(request, ItemTypes.PRF)
