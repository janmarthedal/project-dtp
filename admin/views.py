from django.shortcuts import render

def index(request):
    return render(request, 'admin/index.html')

def recalc_deps(request):
    pass

