import re
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_safe, require_http_methods

from mathitems.models import ItemTypes, MathItem
from validations.models import ItemValidation, Source

import logging
logger = logging.getLogger(__name__)


class AddValidationForm(forms.Form):
    source_type = forms.ChoiceField(choices=Source.SOURCE_TYPE_CHOICES)
    source_value = forms.CharField(max_length=255)
    location = forms.CharField(max_length=255, required=False)

    def clean(self):
        cleaned_data = super().clean()
        source_type = cleaned_data.get('source_type')
        source_value = cleaned_data.get('source_value')
        if source_type in ['isbn10', 'isbn13']:
            source_value = re.sub(r'[ -]', '', source_value.upper())
            cleaned_data['source_value'] = source_value
        if source_type == 'isbn10':
            if not re.match(r'^[0-9]{9}[0-9X]$', source_value):
                self.add_error('source_value', 'Illegal ISBN-10 format')
            digits = [10 if c == 'X' else ord(c)-ord('0') for c in source_value]
            if sum((10-n)*v for n, v in enumerate(digits)) % 11:
                self.add_error('source_value', 'Illegal ISBN-10 checksum')
        elif source_type == 'isbn13':
            if not re.match(r'^[0-9]{12}[0-9X]$', source_value):
                self.add_error('source_value', 'Illegal ISBN-13 format')
            digits = [ord(c)-ord('0') for c in source_value]
            if sum((3 if n % 2 else 1) * v for n, v in enumerate(digits)) % 10:
                self.add_error('source_value', 'Illegal ISBN-13 checksum')


@require_safe
def show_item(request, id_str):
    try:
        item = MathItem.objects.get_by_name(id_str)
    except MathItem.DoesNotExist:
        raise Http404('Item does not exist')
    item_data = item.render()
    context = {
        'title': str(item),
        'item': item,
        'item_data': item_data,
        'validations': item.itemvalidation_set.all()
    }
    if item.item_type == ItemTypes.THM:
        context['new_proof_link'] = reverse('new-prf', args=[item.get_name()])
        context['proofs'] = list(MathItem.objects.filter(item_type=ItemTypes.PRF, parent=item).order_by('id'))
    return render(request, 'mathitems/show.html', context)


@login_required
@require_http_methods(['GET', 'HEAD', 'POST'])
def add_item_validation(request, id_str):
    try:
        item = MathItem.objects.get_by_name(id_str)
    except MathItem.DoesNotExist:
        raise Http404('Item does not exist')
    item_data = item.render()
    if request.method == 'POST':
        form = AddValidationForm(request.POST)
        if form.is_valid():
            source, _ = Source.objects.get_or_create(source_type=form.cleaned_data['source_type'],
                                                     source_value=form.cleaned_data['source_value'])
            item_validation = ItemValidation.objects.create(created_by=request.user,
                                                            item=item,
                                                            source=source,
                                                            location=form.cleaned_data['location'])
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
