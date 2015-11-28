from django.conf.urls import include, url
import main.views

urlpatterns = [
    url(r'^create/(\w+)$', main.views.create_item),
    url(r'^([DTP]\d+)$', main.views.view_item, name='view-item'),
]
