import json
import logging
from functools import wraps
from django.http import HttpResponse, HttpResponseBadRequest

class ApiError(Exception):
    pass

class ApiAuthenticationError(ApiError):
    pass

def api_view(f):
    @wraps(f)
    def wrapper(request, *args, **kwds):
        request.data = json.loads(request.body)
        try:
            return f(request, *args, **kwds)
        except KeyError as e:
            msg = "Key '%s' missing" % e
        except ValueError as e:
            msg = "Value for '%s' is of wrong type or value" % e
        except ApiError as e:
            msg = e
        logger = logging.getLogger(f.__module__)
        logger.warn("In '%s': %s" % (f.__name__, msg))
        return HttpResponseBadRequest()
    return wrapper

def check_string(value):
    return isinstance(value, basestring)

def check_in(value, allowed):
    return value in allowed

def check_category(value):
    return all(check_string(tag_name) for tag_name in value)

def check_category_list(value):
    return all(check_category(c) for c in value)

def api_user(request):
    user = request.user
    if not user.is_authenticated():
        raise ApiAuthenticationError('User not authenticated')
    return user

def api_request_value(request, key, validator):
    try:
        value = request.data[key]
        if validator(value):
            return value
    except (ValueError, TypeError):
        pass
    raise ValueError(key)

def api_request_string(request, key):
    return api_request_value(request, key, check_string)

def api_request_string_option(request, key, allowed):
    return api_request_value(request, key, lambda v: check_string(v) and check_in(v, allowed))

def api_request_category_list(request, key):
    return api_request_value(request, key, check_category_list)
    

def json_response(result):
    return HttpResponse(json.dumps(result), content_type="application/json")
