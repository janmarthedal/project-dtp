from django.shortcuts import render
from django.views.decorators.http import require_safe
from django import forms
from items.helpers import TagListField

@require_safe
def index(request):
    return render(request, 'media/index.html')    


class UploadFileForm(forms.Form):
    file = forms.FileField()
    tags = TagListField(widget=forms.Textarea(attrs={'class': 'tags'}), required=False)
    
    
@require_safe
def add(request):
    form = UploadFileForm()
    return render(request, 'media/add.html', { 'form': form })
