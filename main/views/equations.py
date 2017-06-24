from django.db.models import Count
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_safe

from equations.models import Equation
from mathitems.models import MathItem


@require_safe
def home(request):
    return render(request, 'equations/home.html', {
        'equations': Equation.objects.annotate(use_count=Count('itemequation')).order_by('id')
    })


@require_safe
def show(request, id_str):
    try:
        eqn = Equation.objects.get(pk=id_str)
    except Equation.DoesNotExist:
        raise Http404('Equation does not exist')
    return render(request, 'equations/show.html', {
        'title': 'Equation {}'.format(eqn.pk),
        'eqn': eqn,
        'used_by': MathItem.objects.filter(itemequation__equation=eqn).order_by('id')
    })
