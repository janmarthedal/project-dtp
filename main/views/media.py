import os
from shutil import move
import subprocess
import tempfile
from uuid import uuid4
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_safe, require_http_methods

from keywords.models import Keyword, MediaKeyword
from main.elasticsearch import index_media, item_search
from main.views.helpers import prepare_media_view_list
from media.models import Media
from userdata.permissions import has_perm, require_perm

import logging
logger = logging.getLogger(__name__)

SVGO_EXE_PATH = os.path.join(settings.BASE_DIR, './node_modules/.bin/svgo')
PAGE_SIZE = 25


@require_safe
def home(request):
    return render(request, 'media/home.html', {
        'title': 'Media',
        'items': prepare_media_view_list(Media.objects.order_by('id'))
    })


@require_http_methods(['GET', 'POST'])
@login_required
@require_perm('media')
def media_add(request):
    context = {'title': 'Add Media'}
    if request.method == 'GET':
        pass
    elif 'file' in request.POST:
        curpath = request.POST['file']
        format = 'svg'
        media = Media.objects.create(created_by=request.user, format=format, path=curpath)
        newpath = '{}.{}'.format(media.get_name(), format)
        move(os.path.join(settings.MEDIA_ROOT, curpath),
             os.path.join(settings.MEDIA_ROOT, newpath))
        media.path = newpath
        media.save()
        return redirect('media-home')
    else:
        src = request.FILES['file']
        with tempfile.NamedTemporaryFile(mode='w+b', prefix='mathitems-', delete=False) as dst:
            tmpname = dst.name
            for chunk in src.chunks():
                dst.write(chunk)
        filename = '{}.svg'.format(uuid4().hex)
        cp = subprocess.run([SVGO_EXE_PATH, '--pretty', tmpname,
                             '-o', os.path.join(settings.MEDIA_ROOT, filename)],
                            stderr=subprocess.PIPE)
        if 'error' in cp.stderr.decode().lower():
            context['error'] = 'Not a valid SVG file'
        else:
            context['url'] = settings.MEDIA_URL + filename
            context['field_value'] = filename
    return render(request, 'media/add.html', context)


@require_safe
def show_media(request, media_str):
    try:
        media = Media.objects.get_by_name(media_str)
    except Media.DoesNotExist:
        raise Http404('Media does not exist')
    return render(request, 'media/show.html', {
        'title': 'Media {}'.format(media.get_name()),
        'url': media.full_path(),
        'keywords': Keyword.objects.filter(mediakeyword__media=media).order_by('name').all(),
        'kw_edit_link': has_perm('keyword', request.user) and reverse('edit-media-keywords', args=[media.get_name()])
    })


@require_http_methods(['GET', 'POST'])
@login_required
@require_perm('keyword')
def edit_media_keywords(request, id_str):
    try:
        media = Media.objects.get_by_name(id_str)
    except Media.DoesNotExist:
        raise Http404('Item does not exist')
    if request.method == 'POST':
        if 'delete' in request.POST:
            itemkw = MediaKeyword.objects.get(pk=int(request.POST['delete']))
            itemkw.delete()
        else:
            if request.POST['kw']:
                keyword, _ = Keyword.objects.get_or_create(name=request.POST['kw'])
                itemkw, _ = MediaKeyword.objects.get_or_create(
                                media=media, keyword=keyword, defaults={'created_by': request.user})
        index_media(media)
    context = {
        'title': 'Media {}'.format(media.get_name()),
        'url': media.full_path(),
        'mediakeywords': MediaKeyword.objects.filter(media=media).order_by('keyword__name').all(),
    }
    return render(request, 'media/edit-keywords.html', context)


@require_safe
def media_search(request):
    query = request.GET['q']
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        return redirect('{}?q={}'.format(reverse('media-search'), query))
    if query:
        results, total = item_search(query, 'media', PAGE_SIZE*(page-1), PAGE_SIZE)
        items = [Media.objects.get_by_name(name) for name in results]
        pages_total = (total + PAGE_SIZE - 1)//PAGE_SIZE
    else:
        items = []
        pages_total = 0
    if page > pages_total:
        return redirect('{}?q={}&page={}'.format(reverse('media-search'), query, pages_total))
    return render(request, 'media/media-search-page.html', {
        'title': 'Media search',
        'query': query,
        'items': prepare_media_view_list(items),
        'page_number': page,
        'pages_total': pages_total,
        'prev_link': page > 1 and '?q={}&page={}'.format(query, page-1),
        'next_link': page < pages_total and '?q={}&page={}'.format(query, page + 1),
    })
