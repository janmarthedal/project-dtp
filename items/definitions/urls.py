from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^add$', 'drafts.views.new', { 'kind': 'definition' }),
    url(r'^for/(.*)$', 'tags.views.list_definitions'),
    url(r'^$', 'items.definitions.views.index'),
)
