from django.conf.urls import patterns, url

urlpatterns = patterns('items',
    url(r'^add$',          'views.new', { 'kind': 'definition' }),
    url(r'^concept/(.+)$', 'definitions.views.concept_search'),
    url(r'^$',             'definitions.views.index'),
)

