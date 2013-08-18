from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^add/(?P<parent>\w+)$', 'drafts.views.new', { 'kind': 'proof' }),
    url(r'^$',                    'items.proofs.views.index'),
)


