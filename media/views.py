from django.shortcuts import render
from django.views.decorators.http import require_safe
from django import forms
from main.helpers import init_context

@require_safe
def index(request):
    c = init_context('media')
    return render(request, 'media/index.html', c)

class UploadFileForm(forms.Form):
    file = forms.FileField()

@require_safe
def add(request):
    c = init_context('media')
    form = UploadFileForm()
    c['form'] = form
    return render(request, 'media/add.html', c)
