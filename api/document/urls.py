from django.conf.urls import patterns, url

urlpatterns = patterns('api.document.views',
    url(r'^(\d+)/add-concept$', 'add_concept'),
    url(r'^(\d+)/delete$',      'delete'),
    url(r'^(\d+)',              'sync'),
)
