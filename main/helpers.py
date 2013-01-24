from users.helpers import get_user_info

def init_context(request):
    c = {}
    if request.user.is_authenticated():
        c['auth'] = get_user_info(request.user)
    return c

# assumes the datetime dt is in UTC with no tzinfo
def datetime_user_string(user, dt):
    return dt.replace(microsecond=0).isoformat(' ') + ' UTC'

