from django.db.models import Max
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods, require_safe

from documents.models import Document, DocumentItem
from mathitems.models import MathItem
from userdata.permissions import Perms, require_perm


@require_perm(Perms.DOCUMENT)
@require_http_methods(['HEAD', 'GET', 'POST'])
def add_item(request, item_name):
    try:
        item = MathItem.objects.get_by_name(item_name)
    except MathItem.DoesNotExist:
        raise Http404('Item does not exist')
    if request.method == 'POST':
        if 'addto' in request.POST:
            document = Document.objects.get(id=int(request.POST['addto']))
        else:
            document = Document.objects.create(created_by=request.user, name='Untitled')
            document.name = 'Document {}'.format(document.pk)
            document.save()
        info = DocumentItem.objects.filter(document=document).aggregate(Max('order'))
        m = info['order__max'] or 0
        DocumentItem.objects.create(document=document, item=item, order=m+10)
        return redirect('doc-show', document.pk)
    return render(request, 'documents/add-item.html', {
        'title': 'Add {} to Document'.format(item.get_name()),
        'documents': Document.objects.filter(created_by=request.user).order_by('created_at'),
    })


@require_safe
def show(request, doc_id):
    try:
        document = Document.objects.get(id=int(doc_id))
    except Document.DoesNotExist:
        raise Http404('Document does not exist')
    from django.http import HttpResponse
    return HttpResponse('Document: {}'.format(document))
