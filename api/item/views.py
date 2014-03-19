from django.views.decorators.http import require_POST, require_http_methods
from api.helpers import (ApiError, api_view, api_request_user, api_request_string_list_list,
                         api_request_tag_category_list, api_request_string, api_request_int)
from items.models import FinalItem, ItemValidation, UserItemValidation

@require_http_methods(['PUT'])
@api_view
def final_id(request, item_id):
    user = api_request_user(request)
    # TODO: Check user has permission to update final item

    primary_categories = api_request_string_list_list(request, 'pricats')
    secondary_categories = api_request_string_list_list(request, 'seccats')
    tag_category_map = api_request_tag_category_list(request, 'tagcatmap')

    item = FinalItem.objects.get(final_id=item_id)

    if item.status != 'F':
        raise ApiError('Wrong status')

    item.update(user, primary_categories, secondary_categories, tag_category_map)

    return {
        'id': item.final_id,
        'pricats': primary_categories,
        'seccats': secondary_categories,
        'tagcatmap': tag_category_map
    }

@require_POST
@api_view
def validation_vote(request, item_id):
    user = api_request_user(request)
    validation_id = api_request_int(request, 'validation')
    vote = api_request_string(request, 'vote')
    value = -1 if vote == 'down' else 1 if vote == 'up' else 0
    validation = ItemValidation.objects.get(id=validation_id, item__final_id=item_id)
    UserItemValidation.objects.filter(created_by=user, validation=validation).delete()
    if value:
        UserItemValidation.objects.create(created_by=user, validation=validation, value=value)
    validation.update_points()
    return {
        'validation_points': validation.points,
        'item_points': validation.item.points
    }
