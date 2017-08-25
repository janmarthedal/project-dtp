from hashlib import pbkdf2_hmac
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.http import HttpResponse
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_safe
from django.http import FileResponse

from main.item_helpers import item_to_markup
from main.management.commands.backup import Command as BackupCommand
from userdata.permissions import has_perm, Perms
from mathitems.models import MathItem


KEY_DATETIME_FORMAT = '%Y%m%d%H%M%S'


@require_safe
def datadump(request):
    return HttpResponse(''.join(render_to_string('mathitems/dump.txt', {
        'item': item,
        'markup': item_to_markup(item),
        'validations': item.itemvalidation_set.all()
    }) for item in MathItem.objects.order_by('id')), content_type="text/plain")


def calc_checksum(nonce):
    return pbkdf2_hmac('sha256', settings.SECRET_KEY.encode(),
                       nonce.encode(), 100000).hex()


def check_key(key):
    if len(key) != 78:
        return False
    nonce = key[0:14]
    checksum = key[14:78]
    try:
        timestamp = timezone.datetime.strptime(nonce, KEY_DATETIME_FORMAT)
    except ValueError:
        return False
    delta = timezone.now().replace(tzinfo=None) - timestamp
    return (delta.days == 0 and 0 <= delta.seconds <= 30
            and calc_checksum(nonce) == checksum)


def make_key():
    nonce = timezone.now().strftime(KEY_DATETIME_FORMAT)
    checksum = calc_checksum(nonce)
    return nonce + checksum


@require_safe
def backup(request):
    if request.GET.get('key'):
        if check_key(request.GET['key']):
            path = timezone.now().strftime('/tmp/mathitems-%Y%m%d%H%M%S.json')
            with open(path, 'w') as f:
                call_command(BackupCommand(), stdout=f)
            return FileResponse(open(path, 'rb'), content_type='application/json')
    elif has_perm(Perms.ADMIN, request.user):
        return HttpResponse('{}?key={}'.format(reverse('admin-backup'), make_key()),
                            content_type="text/plain")
    raise PermissionDenied()
