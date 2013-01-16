from django.conf.urls import patterns, include, url

urlpatterns = patterns('items.views',
    url(r'^theorem/new$',    'new', { 'kind': 'theorem' }),
    url(r'^definition/new$', 'new', { 'kind': 'definition' }),
    url(r'^show/(\d+)$',     'show'),
)

