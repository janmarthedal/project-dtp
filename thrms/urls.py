from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^admin/', include('admin.urls')),
    url(r'^user/',  include('users.urls')),
    url(r'^item/',  include('items.urls')),
    url(r'^(\w+)$', 'items.views.show_final'),
    url(r'^$',      'main.views.index'),
)

urlpatterns += patterns('items.views',
    url(r'^theorems/add$',               'new', { 'kind': 'theorem' }),
    url(r'^definitions/add$',            'new', { 'kind': 'definition' }),
    url(r'^proofs/add/(?P<parent>\w+)$', 'new', { 'kind': 'proof' }),
)

