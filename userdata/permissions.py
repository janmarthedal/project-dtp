from functools import wraps
from django.core.exceptions import PermissionDenied


class Perms:
    ADMIN = 'admin'
    DRAFT = 'draft'
    PUBLISH = 'publish'
    DELETE = 'delete'
    VALIDATION = 'validation'
    KEYWORD = 'keyword'
    CINDY = 'cindy'


DEFAULT_PERMS = [Perms.DRAFT, Perms.PUBLISH, Perms.VALIDATION]


def has_perm(name, user):
    if not user.is_authenticated:
        return False
    perms = user.userdata.perms.split(',')
    return 'all' in perms or name in perms


def require_perm(perm_name):
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if not has_perm(perm_name, request.user):
                raise PermissionDenied()
            return func(request, *args, **kwargs)
        return inner
    return decorator
