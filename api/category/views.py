from django.views.decorators.http import require_GET
from main.helpers import json_response
from tags.models import Category

@require_GET
def list_sub_categories(request, path):
    tag_list = path.split('/') if path else []
    category = Category.objects.from_tag_names_or_404(tag_list)
    sub_tag_names = list(Category.objects.filter(parent=category).values_list('tag__name', flat=True))
    return json_response(sub_tag_names)
