import json
import logging
from functools import wraps
from django.http import HttpResponse, HttpResponseBadRequest

class ApiAuthenticationError(Exception):
    pass

def api_view(f):
    @wraps(f)
    def wrapper(request, *args, **kwds):
        request.data = json.loads(request.body)
        try:
            return f(request, *args, **kwds)
        except ApiAuthenticationError as e:
            logger = logging.getLogger(f.__module__)
            logger.warn("In '%s': %s" % (f.__name__, e))
            return HttpResponseBadRequest()
    return wrapper

def api_user(request):
    user = request.user
    if not user.is_authenticated():
        raise ApiAuthenticationError('User not authenticated')
    return user

def api_key(request, key):
    if key not in request.data:
        raise ApiAuthenticationError("Key '%s' required in request" % key)
    return request.data[key]

def json_response(result):
    return HttpResponse(json.dumps(result), content_type="application/json")
