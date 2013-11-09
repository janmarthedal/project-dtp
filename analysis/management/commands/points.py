from django.db.models import Sum
from items.models import FinalItem, ItemValidation, UserItemValidation

def update_item_points(fitem):
    assert isinstance(fitem, FinalItem)
    sum_aggregate = ItemValidation.objects.filter(item=fitem, points__gt=0).aggregate(Sum('points'))
    validation_points = sum_aggregate['points__sum'] or 0
    sum_aggregate = FinalItem.objects.filter(parent=fitem, status='F', points__gt=0).aggregate(Sum('points'))
    child_points = sum_aggregate['points__sum'] or 0
    points = 1 + validation_points + child_points
    if points != fitem.points:
        fitem.points = points
        fitem.save()
        if fitem.parent:
            update_item_points(fitem.parent)

def update_validation_points(validation):
    assert isinstance(validation, ItemValidation)
    sum_aggregate = UserItemValidation.objects.filter(validation=validation).aggregate(Sum('value'))
    points = sum_aggregate['value__sum'] or 0
    if points != validation.points:
        validation.points = points
        validation.save()
        update_item_points(validation.item)
