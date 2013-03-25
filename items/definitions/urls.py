from django.conf.urls import patterns, url

urlpatterns = patterns('items',
    url(r'^add$',          'views.new', { 'kind': 'definition' }),
    url(r'^concept/(.+)$', 'definitions.views.concept_search'),
    url(r'^search$',       'definitions.views.search'),
    url(r'^search2$',      'definitions.views.search2'),
    url(r'^$',             'definitions.views.index'),
)

