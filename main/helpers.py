import json
from functools import wraps
from django.http import Http404

def logged_in_or_404(view):
    @wraps(view)
    def wrapper(request, *args, **kwds):
        if not request.user.is_authenticated():
            raise Http404
        return view(request, *args, **kwds)
    return wrapper

"""
def logged_in_or_prompt(message=None):
    def real_decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwds):
            if not request.user.is_authenticated():
                if message:
                    messages.info(request, message)
                return HttpResponseRedirect(reverse('users.views.login') + '?next=' + request.path)
            return view(request, *args, **kwds)
        return wrapper
    return real_decorator
"""

def init_context(nav, extra={}, **kwargs):
    if   nav.upper() == 'D': nav = 'definitions'
    elif nav.upper() == 'T': nav = 'theorems'
    elif nav.upper() == 'P': nav = 'proofs'
    c = { 'active_nav': nav }
    c.update(extra)
    c.update(**kwargs)
    return c

class ListWrapper(object):

    def __init__(self, iterable):
        self._list = list(iterable)

    def __len__(self):
        return len(self._list)

    def __getitem__(self, key):
        return self._list[key]

    def __iter__(self):
        return self._list.__iter__()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def __unicode__(self):
        return unicode(self.json_serializable())

    def json_serializable(self):
        return self._list

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return obj.json_serializable()
        except AttributeError:
            return json.JSONEncoder.default(self, obj)

def json_encode(obj):
    return json.dumps(obj, cls=CustomJSONEncoder)

def json_decode(st):
    return json.loads(st)
