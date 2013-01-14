def init_context(request):
    c = {}
    if request.user.is_authenticated():
        c['username'] = request.user.username
    return c

