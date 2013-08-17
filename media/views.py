import uuid
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_safe, require_http_methods
from main.helpers import init_context

import logging
logger = logging.getLogger(__name__)

@require_safe
def index(request):
    c = init_context('media')
    return render(request, 'media/index.html', c)

class UploadFileForm(forms.Form):
    file = forms.FileField()

def handle_uploaded_file(f):
    filename = settings.MEDIA_ROOT + uuid.uuid4().hex
    with open(filename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

@require_http_methods(["GET", "POST"])
def add(request):
    c = init_context('media')
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            logger.info('media/add form valid')
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect(reverse('media.views.index'))
        logger.info('media/add form invalid')
    else:
        logger.info('media/add form clean')
        form = UploadFileForm()
    c['form'] = form
    return render(request, 'media/add.html', c)
