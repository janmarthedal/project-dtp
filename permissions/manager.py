from permissions.models import Permission

def has_perm(name, user):
    if not user.is_authenticated:
        return False

    permission = Permission.objects.get(name=name)

    return permission.users.filter(id=user.id).exists()
