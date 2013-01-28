def init_context(request):
    return {}

# assumes the datetime dt is in UTC with no tzinfo
def datetime_user_string(user, dt):
    return dt.replace(microsecond=0).isoformat(' ')

