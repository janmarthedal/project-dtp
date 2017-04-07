from functools import wraps
from django.core.exceptions import PermissionDenied


def has_perm(name, user):
    return user.is_authenticated and name in user.userdata.perms.split(',')


def require_perm(perm_name):
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if not has_perm(perm_name, request.user):
                raise PermissionDenied()
            return func(request, *args, **kwargs)
        return inner
    return decorator
