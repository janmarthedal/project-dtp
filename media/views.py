import os
import string
import subprocess
import tempfile
import uuid
from collections import namedtuple
from django import forms
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_safe, require_http_methods
from main.helpers import init_context, logged_in_or_prompt
from media.models import MediaEntry, MediaItem

import logging
logger = logging.getLogger(__name__)

THUMB_WIDTH = 256
THUMB_HEIGHT = 128

def handle_upload(f):
    filepath = tempfile.gettempdir() + '/' + uuid.uuid4().hex
    with open(filepath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return filepath

"""
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if not (exc.errno == errno.EEXIST and os.path.isdir(path)):
            raise
"""

MediaFileMetaData = namedtuple('MediaFileMetaData', ['format', 'width', 'height'])

def absolute_media_path(relative_path):
    return settings.MEDIA_ROOT + '/' + relative_path

def move_to_media_folder(tmpname, extension):
    for _ in range(0, 10):
        filename = '%s.%s' % (get_random_string(8, string.digits), extension)
        try:
            os.rename(tmpname, absolute_media_path(filename))
            return filename
        except OSError:
            pass
    raise Exception('move_to_media_folder')

def get_media_file_meta_data(filename):
    try:
        format_data = subprocess.check_output(['identify', '-format', '%m %w %h', filename])
        format_items = format_data.strip().split(' ')
        media_format = format_items[0].lower()
        width = int(format_items[1])
        height = int(format_items[2])
        return MediaFileMetaData(format=media_format, width=width, height=height)
    except subprocess.CalledProcessError:
        return MediaFileMetaData(format='unknown', width=None, height=None)

def make_thumbnail(filename):
    tmpname = tempfile.gettempdir() + '/' + uuid.uuid4().hex + '.png'
    try:
        subprocess.check_call(['convert', absolute_media_path(filename),
                               '-thumbnail', '%dx%d' % (THUMB_WIDTH, THUMB_HEIGHT), tmpname])
        return tmpname
    except:
        raise Exception('make_thumbnail')

def is_thumbnail_image(meta_data):
    return (meta_data.format == 'png' and
            ((meta_data.width == THUMB_WIDTH and meta_data.height <= THUMB_HEIGHT) or
             (meta_data.width <= THUMB_WIDTH and meta_data.height == THUMB_HEIGHT)))

class UploadFileForm(forms.Form):
    file = forms.FileField()

@require_safe
def index(request):
    items = []
    for entry in MediaEntry.objects.all():
        try:
            item = MediaItem.objects.get(entry=entry, itemtype='T')
            link = settings.MEDIA_URL + item.path
        except MediaItem.DoesNotExist:
            link = None
        items.append(dict(public_id=entry.public_id, link=link))
    c = init_context('media', items=items)
    return render(request, 'media/index.html', c)

@logged_in_or_prompt('You need to log in to add media')
@require_http_methods(["GET", "POST"])
def add(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            tmpname = handle_upload(request.FILES['file'])
            meta_data = get_media_file_meta_data(tmpname)
            if meta_data.format not in ['png', 'jpg', 'jpeg', 'gif', 'svg']:
                messages.info(request, 'Unable to upload media: Unsupported file type')
                return HttpResponseRedirect(reverse('media.views.index'))
            filepath = move_to_media_folder(tmpname, meta_data.format)
            entry = MediaEntry.objects.add_entry(request.user)
            MediaItem.objects.create(entry=entry, path=filepath, itemtype='O',
                                     format=meta_data.format,
                                     width=meta_data.width, height=meta_data.height)
            tmpname = make_thumbnail(filepath)
            meta_data = get_media_file_meta_data(tmpname)
            assert is_thumbnail_image(meta_data)
            filepath = move_to_media_folder(tmpname, meta_data.format)
            MediaItem.objects.create(entry=entry, path=filepath, itemtype='T',
                                     format=meta_data.format,
                                     width=meta_data.width, height=meta_data.height)
            return HttpResponseRedirect(reverse('media.views.view', args=[entry.public_id]))
    else:
        form = UploadFileForm()
    c = init_context('media', form=form)
    return render(request, 'media/add.html', c)

@require_safe
def view(request, media_id):
    entry = get_object_or_404(MediaEntry, public_id=media_id)
    item = get_object_or_404(MediaItem, entry=entry, itemtype='O')
    c = init_context('media', public_id=entry.public_id, link=settings.MEDIA_URL + item.path)
    return render(request, 'media/view.html', c)
