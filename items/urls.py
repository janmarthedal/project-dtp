from django.conf.urls import patterns, include, url

urlpatterns = patterns('items.views',
    url(r'^add/theorem$',               'new', { 'kind': 'theorem' }),
    url(r'^add/definition$',            'new', { 'kind': 'definition' }),
    url(r'^add/proof/(?P<parent>\w+)$', 'new', { 'kind': 'proof' }),
    url(r'^show/(\d+)$',                'show'),
    url(r'^edit/(\d+)$',                'edit'),
    url(r'^change_status$',             'change_status'),
)

