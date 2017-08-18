from functools import wraps
from django.core.exceptions import PermissionDenied


PERM_ADMIN = 'admin'
PERM_DRAFT = 'draft'
PERM_PUBLISH = 'publish'
PERM_DELETE = 'delete'
PERM_VALIDATION = 'validation'
PERM_KEYWORD = 'keyword'


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
