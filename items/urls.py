from django.conf.urls import patterns, include, url

urlpatterns = patterns('items.views',
    url(r'^new/theorem$',    'new', { 'kind': 'theorem' }),
    url(r'^new/definition$', 'new', { 'kind': 'definition' }),
    url(r'^show/(\d+)$',     'show'),
    url(r'^edit/(\d+)$',     'edit'),
    url(r'^change_status$',  'change_status'),
)

