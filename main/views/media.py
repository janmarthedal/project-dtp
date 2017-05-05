import os
from shutil import move
import subprocess
import tempfile
import json
from uuid import uuid4
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_safe, require_http_methods

from keywords.models import Keyword, MediaKeyword
from main.elasticsearch import index_media, item_search
from main.views.helpers import prepare_media_view_list, LIST_PAGE_SIZE
from media.models import Media
from project.server_com import parse_cindy
from userdata.permissions import has_perm, require_perm

import logging
logger = logging.getLogger(__name__)

SVGO_EXE_PATH = os.path.join(settings.BASE_DIR, './node_modules/.bin/svgo')


@require_safe
def home(request):
    return render(request, 'media/home.html', {
        'title': 'Media',
        'items': prepare_media_view_list(Media.objects.order_by('id'))
    })


def validate_svg(tmpname):
    filename = '{}.svg'.format(uuid4().hex)
    cp = subprocess.run([SVGO_EXE_PATH, '--pretty', tmpname,
                         '-o', os.path.join(settings.MEDIA_ROOT, filename)],
                        stderr=subprocess.PIPE)
    if 'error' in cp.stderr.decode().lower():
        return None, None
    return filename, 'svg'


def validate_cindy(tmpname):
    result = parse_cindy(tmpname)
    if 'error' in result:
        return None, None

    data = result['data']
    if 'ports' in data:
        if type(data['ports']) is not list or len(data['ports']) != 1:
            return None, None
    else:
        data['ports'] = [{}]
    for key in ['width', 'height']:
        if key in data['ports'][0]:
            del data['ports'][0][key]
    data['ports'][0]['id'] = 'cscanvas'
    data['ports'][0]['fill'] = 'window'
    if 'scripts' in data:
        del data['scripts']

    filename = '{}.html'.format(uuid4().hex)
    content = render_to_string('media/cindy-media.html', {
        'title': result['title'],
        'lib': result['lib'],
        'data': '{{\n{}\n}}'.format(',\n'.join('  "{}": {}'.format(k, json.dumps(v)) for k, v in data.items()))
    })
    with open(os.path.join(settings.MEDIA_ROOT, filename), 'w') as dst:
        dst.write(content)
    return filename, 'cindy'


@require_http_methods(['GET', 'POST'])
@login_required
@require_perm('media')
def media_add(request):
    context = {'title': 'Add Media'}
    if request.method == 'GET':
        pass
    elif 'file' in request.POST:
        curpath = request.POST['file']
        format = request.POST['format']
        media = Media.objects.create(created_by=request.user, format=format, path=curpath)
        newpath = '{}.{}'.format(media.get_name(), {'svg': 'svg', 'cindy': 'html'}[format])
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

        filename, format = validate_svg(tmpname)

        if format is None:
            filename, format = validate_cindy(tmpname)

        if format is not None:
            url = settings.MEDIA_URL + filename
            if format == 'svg':
                context['tag'] = '<img class="item-img" src="{}">'.format(url)
            else:
                context['tag'] = '''<div style="position: relative; width: 100%; height: 0; padding-bottom: 53.3%;">
  <iframe style="position: absolute; width: 100%; height: 100%; left: 0; top: 0;" src="{}"></iframe>
</div>'''.format(url)
            context['field_value'] = filename
            context['format'] = format
        else:
            context['error'] = 'Not a recognized media format'
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
        results, total = item_search(query, 'media', LIST_PAGE_SIZE*(page-1), LIST_PAGE_SIZE)
        items = [Media.objects.get_by_name(name) for name in results]
        pages_total = (total + LIST_PAGE_SIZE - 1)//LIST_PAGE_SIZE
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
