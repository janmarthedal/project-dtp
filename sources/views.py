from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_safe, require_http_methods
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django import forms
from items.models import FinalItem
from sources.models import RefNode, RefAuthor, SourceValidation
from main.helpers import init_context, logged_in_or_404


@require_safe
def index(request):
    c = init_context('sources')
    c['sourcelist'] = RefNode.objects.all()
    return render(request, 'sources/index.html', c)


class AddSourceForm(forms.Form):
    title     = forms.CharField(max_length=256, required=False)
    author1   = forms.CharField(max_length=64, required=False)
    author2   = forms.CharField(max_length=64, required=False)
    author3   = forms.CharField(max_length=64, required=False)
    author4   = forms.CharField(max_length=64, required=False)
    publisher = forms.CharField(max_length=64, required=False)
    year      = forms.IntegerField(min_value=0, max_value=2100, required=False)
    edition   = forms.CharField(max_length=16, required=False)
    series    = forms.CharField(max_length=64, required=False)
    isbn10    = forms.CharField(max_length=10, required=False)
    isbn13    = forms.CharField(max_length=13, required=False)
    extra     = forms.CharField(max_length=256, required=False)

class AddLocation(forms.Form):
    location = forms.CharField(max_length=256)


@logged_in_or_404
@require_http_methods(["GET", "POST"])
def add_source(request, final_id):
    c = init_context('sources')
    item = get_object_or_404(FinalItem, final_id=final_id)
    c['item'] = item
    source = None

    if request.method == 'POST':
        action = request.POST['submit'].lower()

        if 'source' not in request.POST:         # screen 1
            form = AddSourceForm(request.POST)

            if form.is_valid():

                if action == 'search':
                    query = RefNode.objects
                    for field in ['author1', 'author2', 'author3', 'author4']:
                        if form.cleaned_data.get(field):
                            query = query.filter(authors__name__icontains=form.cleaned_data[field])
                    kwargs = {}
                    for field in ['title', 'isbn10', 'isbn13', 'publisher', 'series',
                                  'edition', 'year', 'extra']:
                        if form.cleaned_data.get(field):
                            kwargs['%s__icontains' % field] = form.cleaned_data[field]
                    if kwargs:
                        query = query.filter(kwargs)
                    c['search'] = { 'results': query.all() }

                elif action == 'next':
                    source = RefNode(created_by=request.user)
                    for field in ['title', 'isbn10', 'isbn13', 'publisher', 'series',
                                  'edition', 'year', 'extra']:
                        if form.cleaned_data.get(field):
                            source.__dict__[field] = form.cleaned_data[field]
                    source.save()

                    author_names = set(map(form.cleaned_data.get, ['author1', 'author2', 'author3', 'author4'])) - set([''])
                    author_list = [RefAuthor.objects.get_or_create(name=name)[0] for name in author_names]
                    source.authors = author_list
                    source.save()

                    form = AddLocation()

        else:                                    # screen 2
            form = AddLocation(request.POST)
            source = get_object_or_404(RefNode, pk=request.POST['source'])

            if form.is_valid():

                if action == 'preview':
                    pass

                else:  # add validation
                    source_validation = SourceValidation(created_by=request.user,
                                                         item=item,
                                                         source=source,
                                                         location=form.cleaned_data['location'])
                    source_validation.save()
                    return HttpResponseRedirect(reverse('items.views.show_final', args=[item.final_id]))

    elif 'source' in request.GET:
        source = get_object_or_404(RefNode, pk=request.GET['source'])
        form = AddLocation()

    else:
        form = AddSourceForm()

    c.update({ 'form': form, 'source': source })
    return render(request, 'sources/add_source.html', c)

@require_safe
def add_source2(request):
    c = init_context('sources')
    return render(request, 'sources/add_source2.html', c)
