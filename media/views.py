import errno
import os
import string
import subprocess
import tempfile
import uuid
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_safe, require_http_methods
from main.helpers import init_context, logged_in_or_prompt
from media.models import MediaEntry, MediaItem

import logging
logger = logging.getLogger(__name__)

class UploadFileForm(forms.Form):
    file = forms.FileField()

def handle_upload(f):
    filepath = tempfile.gettempdir() + '/' + uuid.uuid4().hex
    with open(filepath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return filepath

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if not (exc.errno == errno.EEXIST and os.path.isdir(path)):
            raise

def move_to_media_folder(tmpname, extension):
    for length in range(4, 10+1):
        filename = 'M%s.%s' % (get_random_string(length, string.digits), extension)
        try:
            os.rename(tmpname, settings.MEDIA_ROOT + '/' + filename)
            return filename
        except OSError:
            pass
    raise Exception('move_to_media_folder')

def move_file_to_entry(entry, tmpname):
    format_data = subprocess.check_output(['identify', '-format', '%m %w %h', tmpname])
    format_items = format_data.strip().split(' ')
    media_format = format_items[0]
    width = int(format_items[1])
    height = int(format_items[2])
    if MediaItem.objects.filter(entry=entry, format=media_format, width=width, height=height).exists():
        return
    filepath = move_to_media_folder(tmpname, media_format.lower())
    MediaItem.objects.create(entry=entry, path=filepath,
                             format=media_format, width=width, height=height)

@require_safe
def index(request):
    c = init_context('media')
    return render(request, 'media/index.html', c)

@logged_in_or_prompt('You need to log in to add media')
@require_http_methods(["GET", "POST"])
def add(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            logger.info('media/add form valid')
            filepath = handle_upload(request.FILES['file'])
            entry = MediaEntry.objects.create(created_by=request.user)
            move_file_to_entry(entry, filepath)
            return HttpResponseRedirect(reverse('media.views.index'))
        logger.info('media/add form invalid')
    else:
        logger.info('media/add form clean')
        form = UploadFileForm()
    c = init_context('media', form=form)
    return render(request, 'media/add.html', c)
