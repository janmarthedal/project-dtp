from django.core import management
from users.models import Invitations

class Command(management.base.BaseCommand):
    args = 'target-email [target-name]'
    help = 'Create and send an invitation by email'

    def handle(self, target_email, target_name=None, **options):
        invite = Invitations.objects.make_invitation(target_email=target_email, target_name=target_name)
        self.stdout.write('Invitation created: {}'.format(invite))
        invite.send()
