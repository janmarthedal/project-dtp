from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^add$', 'drafts.views.new', {'kind': 'definition'}),
    url(r'^for/(.*)$', 'tags.views.definitions_in_category'),
    url(r'^$', 'items.definitions.views.index'),
    url(r'^most-wanted$', 'items.definitions.views.most_wanted'),
)
