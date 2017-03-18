from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from permissions.models import Permission


class Command(BaseCommand):
    help = 'Edit user permissions'

    def handle(self, *args, **options):
        self.stdout.write('\nChoose user:')
        User = get_user_model()
        for user in User.objects.order_by('id'):
            self.stdout.write('  {}. {}'.format(user.id, user.username))

        user_id = input('\n>> ')
        if not user_id: return

        user = User.objects.get(id=int(user_id))

        self.stdout.write('Editing user {}'.format(user.username))

        while True:
            for perm in Permission.objects.order_by('name').all():
                self.stdout.write('  {}. {}  {}'.format(perm.id, perm.name,
                    'ON' if perm.users.filter(id=user.id).exists() else 'OFF'))

            perm_id = input('\n>> ')
            if not perm_id: return

            perm = Permission.objects.get(id=int(perm_id))

            if perm.users.filter(id=user.id).exists():
                perm.users.remove(user)
            else:
                perm.users.add(user)
