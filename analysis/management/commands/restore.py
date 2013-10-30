import shutil
import tarfile
import tempfile
from django.conf import settings
from django.core import management
from analysis.management.commands import backup

class Command(management.base.BaseCommand):
    help = 'Data restore'

    def handle(self, archivename, *args, **options):
        tmpdir = tempfile.mkdtemp()
        self.stdout.write(tmpdir)
        with tarfile.open(archivename, "r:*") as tar:
            tar.extractall(path=tmpdir)
        management.call_command('loaddata', tmpdir + '/' + backup.FIXTURE_NAME)
        shutil.rmtree(settings.MEDIA_ROOT)
        shutil.copytree(tmpdir + '/' + backup.MEDIA_NAME, settings.MEDIA_ROOT)
        shutil.rmtree(tmpdir)
