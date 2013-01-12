from django.shortcuts import render
from main.models import Item, ItemTag, Tag

def index(request):
    #latest_items = Item.objects.filter(status='F').order_by('-modified_at')[:10]
    #latest_item_list = [{
    #    'link': item.get_absolute_url(),
    #    'name': item.get_cap_kind_with_id()
    #} for item in latest_items]
    return render(request, 'thrms/index.html')

