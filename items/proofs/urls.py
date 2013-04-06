from django.conf.urls import patterns, url

urlpatterns = patterns('items',
    url(r'^add/(?P<parent>\w+)$', 'views.new', { 'kind': 'proof' }),
    url(r'^$',                    'proofs.views.index'),
)


