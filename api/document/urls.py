from django.conf.urls import patterns, url

urlpatterns = patterns('api.document.views',
    url(r'^(\d+)/add-concept$', 'add_concept'),
    url(r'^(\d+)/add-item$',    'add_item'),
    url(r'^(\d+)/delete$',      'delete_item'),
    url(r'^(\d+)$',             'sync'),
    url(r'^$',                  'new'),
)
