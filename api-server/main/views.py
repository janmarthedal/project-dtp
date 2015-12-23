import json
from django.http import JsonResponse

def drafts(request):
    data = json.loads(request.body.decode())
    return JsonResponse(data)
