from django.contrib.auth.decorators import login_required

@login_required
def new_theorem(request):
    pass

@login_required
def new_definition(request):
    pass

