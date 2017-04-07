from django.core.management import call_command
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_safe
from django.http import FileResponse

from main.item_helpers import item_to_markup
from main.management.commands.backup import Command as BackupCommand
from userdata.permissions import require_perm
from mathitems.models import MathItem


@require_safe
def datadump(request):
    return HttpResponse(''.join(render_to_string('mathitems/dump.txt', {
        'item': item,
        'markup': item_to_markup(item),
        'validations': item.itemvalidation_set.all()
    }) for item in MathItem.objects.order_by('id')), content_type="text/plain")


@require_safe
@require_perm('admin')
def backup(request):
    path = timezone.now().strftime('/tmp/mathitems-%Y%m%d%H%M%S.json')
    with open(path, 'w') as f:
        call_command(BackupCommand(), stdout=f)
    return FileResponse(open(path, 'rb'), content_type='application/json')
