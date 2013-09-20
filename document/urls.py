from django.conf.urls import patterns, url

urlpatterns = patterns('document.views',
    url(r'^new$',                'new'),
    url(r'^id/(\d+)$',           'view'),
    url(r'^id/(\d+)/add/(\w+)$', 'add'),
    url(r'^delete$',             'delete'),
)
