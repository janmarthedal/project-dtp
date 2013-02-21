from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^add$',         'items.views.new', { 'kind': 'definition' }),
    url(r'^search/(.+)$', 'items.definitions.views.concept_search'),
    url(r'^$',            'items.definitions.views.index'),
)

