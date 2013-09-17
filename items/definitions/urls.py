from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^add$',              'drafts.views.new', { 'kind': 'definition' }),
    url(r'^list$',             'items.definitions.views.index'),
    url(r'^categorized/(.*)$', 'tags.views.list_definitions'),
)
