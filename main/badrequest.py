from django.views.defaults import bad_request

class BadRequest(Exception):
    pass

class HandleBadRequest:
    def process_exception(self, request, exception):
        if isinstance(exception, BadRequest):
            return bad_request(request)
        return None
