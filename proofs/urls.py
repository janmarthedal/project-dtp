from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^add/(?P<parent>\w+)$', 'items.views.new', { 'kind': 'proof' }),
    url(r'^$',                    'proofs.views.index'),
)


