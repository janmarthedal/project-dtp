import json
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django import forms
from django.forms.formsets import formset_factory
from items.models import Item
from refs.models import RefField, RefAttribute, RefNode
from validate.models import SourceValidation

import logging
logger = logging.getLogger(__name__)

class AttributeForm(forms.Form):
    field = forms.CharField(max_length=32)
    value = forms.CharField(max_length=128)

@login_required
@require_http_methods(["GET", "POST"])
def add_source(request, final_id):
    item = get_object_or_404(Item, final_id=final_id)
    c = { 'item': item }
    AttributeFormSet = formset_factory(AttributeForm, extra=4)
    if request.method == 'POST':
        logger.debug(str(request.POST))
        formset = AttributeFormSet(request.POST)
        if formset.is_valid():
            action = request.POST['submit'].lower()
            if action == 'search':
                logger.debug('search')
            elif action == 'next':
                logger.debug(str(formset.cleaned_data))
                source = [(src['field'], src['value']) for src in formset.cleaned_data
                          if 'field' in src and 'value' in src]
                c['source'] = json.dumps(source)
                formset = AttributeFormSet()
            elif action == 'preview':
                c['source'] = request.POST['source']
            else:  # add validation
                source = json.loads(request.POST['source'].replace('&quot;', '"'))
                logger.debug(source)
                attrs = []
                for src in source:
                    field, created = RefField.objects.get_or_create(name=src[0])
                    attr, created = RefAttribute.objects.get_or_create(field=field, value=src[1])
                    attrs.append(attr)
                refnode = RefNode()
                refnode.save()
                refnode.attributes = attrs
                refnode.save()

                locs = [(src['field'], src['value']) for src in formset.cleaned_data
                        if 'field' in src and 'value' in src]
                
                sourceval = SourceValidation(item=item, source=refnode, created_by=request.user)
                attrs = []
                for src in locs:
                    field, created = RefField.objects.get_or_create(name=src[0])
                    attr, created = RefAttribute.objects.get_or_create(field=field, value=src[1])
                    attrs.append(attr)
                sourceval.save()
                sourceval.location = attrs
                sourceval.save()
                return HttpResponseRedirect(reverse('items.views.show_final', args=[item.final_id]))
        else:
            logger.debug(str(formset.errors))
    else:
        formset = AttributeFormSet(initial=[{'field':'author'}, {'field':'title'}])
    c['formset'] = formset
    return render(request, 'items/add_source.html', c)


