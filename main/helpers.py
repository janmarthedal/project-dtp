from users.helpers import get_user_info

def init_context(request):
    c = {}
    if request.user.is_authenticated():
        c['auth'] = get_user_info(request.user)
    return c

