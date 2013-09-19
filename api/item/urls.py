from django.conf.urls import patterns, url

urlpatterns = patterns('api.item.views',
    url(r'^search$', 'items'),
    url(r'^(\w+)$',  'final_id'),
)
