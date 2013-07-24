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
            result = f(request, *args, **kwds)
            return HttpResponse(json.dumps(result), content_type="application/json")
        except KeyError as e:
            msg = "Key %s missing" % e
        except ValueError as e:
            msg = "Value for '%s' is of wrong type or value" % e
        except ApiError as e:
            msg = e
        logger = logging.getLogger(f.__module__)
        logger.warn("In '%s': %s" % (f.__name__, msg))
        return HttpResponseBadRequest()
    return wrapper


def is_string(value):
    return isinstance(value, basestring)

def is_int(value):
    return isinstance(value, int)

def is_string_list(value):
    return isinstance(value, list) and all(is_string(tag_name) for tag_name in value)

def is_string_list_list(value):
    return isinstance(value, list) and all(is_string_list(c) for c in value)

def is_tag_category(value):
    try:
        return len(value) == 2 and is_string(value['tag']) and is_string_list(value['category'])
    except KeyError:
        return False

def is_tag_category_list(value):
    return isinstance(value, list) and all(is_tag_category(c) for c in value)


def api_request_user(request):
    user = request.user
    if not user.is_authenticated():
        raise ApiAuthenticationError('User not authenticated')
    return user

def api_request_value(request, key, validator):
    value = request.data[key]
    if not validator(value):
        raise ValueError(key)
    return value

def api_request_string(request, key):
    return api_request_value(request, key, is_string)

def api_request_int(request, key):
    return api_request_value(request, key, is_int)

def api_request_string_list_list(request, key):
    return api_request_value(request, key, is_string_list_list)

def api_request_tag_category_list(request, key):
    return api_request_value(request, key, is_tag_category_list)
