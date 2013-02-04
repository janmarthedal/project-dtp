import json
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django import forms
from django.forms.formsets import formset_factory, BaseFormSet
from django.db.models import Count
from items.models import Item
from refs.models import RefField, RefAttribute, RefNode
from validate.models import SourceValidation

import logging
logger = logging.getLogger(__name__)

class AttributeForm(forms.Form):
    field = forms.CharField(max_length=32, required=False)
    value = forms.CharField(max_length=128, required=False)

class AttributeFormSet(BaseFormSet):
    def get_field_value_pairs(self):
        return [src for src in self.cleaned_data
                if 'field' in src and 'value' in src and src['field'] and src['value']]

def make_attribute_list(field_value_pairs):
    attrs = []
    for attr in field_value_pairs:
        field, created = RefField.objects.get_or_create(name=attr['field'].lower())
        attr, created = RefAttribute.objects.get_or_create(field=field, value=attr['value'])
        attrs.append(attr)
    return attrs

def get_or_create_refnode(attrs, user):
    query = RefNode.objects.annotate(attr_count=Count('attributes')).filter(attr_count=len(attrs))
    for attr in attrs:
        query = query.filter(attributes__field__name=attr['field'].lower(),
                             attributes__value=attr['value'])
    if query.count():
        return query[0].pk
    refnode = RefNode(created_by=user)
    refnode.save()
    refnode.attributes = make_attribute_list(attrs)
    refnode.save()
    return refnode

@login_required
@require_http_methods(["GET", "POST"])
def add_source(request, final_id):
    item = get_object_or_404(Item, final_id=final_id)
    c = { 'item': item }
    AttributeFormSetGen = formset_factory(AttributeForm, formset=AttributeFormSet, extra=4)
    if request.method == 'POST':
        formset = AttributeFormSetGen(request.POST)
        if formset.is_valid():
            attrs = formset.get_field_value_pairs()
            action = request.POST['submit'].lower()

            if action == 'search':
                query = RefNode.objects
                for attr in attrs:
                    query = query.filter(attributes__field__name=attr['field'].lower(),
                                         attributes__value__icontains=attr['value'])
                c['search'] = { 'results': list(query) }
                formset = AttributeFormSetGen(initial=attrs)

            elif action == 'next':
                c['source'] = get_or_create_refnode(attrs, request.user)
                formset = AttributeFormSetGen()

            elif action == 'preview':
                c['source'] = get_object_or_404(RefNode, pk=request.POST['source'])
                formset = AttributeFormSetGen(initial=attrs)

            else:  # add validation
                refnode_id = request.POST['source']
                sourceval = SourceValidation(item=item, source=refnode_id, created_by=request.user)
                sourceval.save()
                sourceval.location = make_attribute_list(attrs)
                sourceval.save()
                return HttpResponseRedirect(reverse('items.views.show_final', args=[item.final_id]))

        else:
            logger.debug(str(formset.errors))

    elif 'source' in request.GET:
        c['source'] = get_object_or_404(RefNode, pk=request.GET['source'])
        formset = AttributeFormSetGen()

    else:
        formset = AttributeFormSetGen(initial=[{'field': 'author'}, {'field': 'title'}])

    c['formset'] = formset
    return render(request, 'items/add_source.html', c)


