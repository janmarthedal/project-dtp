from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^add$', 'drafts.views.new', { 'kind': 'definition' }),
    url(r'^$',    'items.definitions.views.index'),
)

