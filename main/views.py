from django.shortcuts import render
from django.views.decorators.http import require_safe
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.conf import settings
from items.models import DraftItem, FinalItem

@require_safe
def index(request):
    if not settings.DEBUG:
        return HttpResponseRedirect(reverse('main.views.signup'))
    return home(request)

@require_safe
def home(request):
    c = {
        'finalitems':  list(FinalItem.objects.filter(status='F').order_by('-created_at')),
        'reviewitems': list(DraftItem.objects.filter(status='R').order_by('-modified_at')),
        }
    return render(request, 'home.html', c)

@require_safe
def signup(request):
    return render(request, 'signup.html')