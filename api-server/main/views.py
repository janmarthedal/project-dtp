from django.http import JsonResponse

def drafts(request):
    return JsonResponse({'ok': True})
