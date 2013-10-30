import os
import tarfile
import tempfile
from django.conf import settings
from django.core import management
from django.utils import timezone

FIXTURE_NAME='db.json'
MEDIA_NAME='media'

class Command(management.base.BaseCommand):
    help = 'Data backup'

    def handle(self, outname=None, *args, **options):
        if not outname:
            outname = timezone.now().strftime('%Y-%m-%d-%H-%M.tar.gz')
        apps = ['users', 'tags', 'drafts', 'items', 'sources']
        with tarfile.open(outname, "w:gz") as tar:
            tf = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
            management.call_command('dumpdata', *apps, indent=2, stdout=tf)
            tf.close()
            tar.add(tf.name, arcname=FIXTURE_NAME)
            tar.add(settings.MEDIA_ROOT, arcname=MEDIA_NAME)
            os.remove(tf.name)
