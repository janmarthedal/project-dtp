from django.conf.urls import include, url
import main.views

urlpatterns = [
    url(r'^create/(\w+)$', main.views.create_item),
    url(r'^drafts/$', main.views.drafts_home),
    url(r'^drafts/(\d+)$', main.views.view_draft, name='view-draft'),
    #url(r'^([DTP]\d+)$', main.views.view_item, name='view-item'),
]
