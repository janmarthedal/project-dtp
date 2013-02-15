from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^add$',                 'items.views.new', { 'kind': 'definition' }),
    url(r'^search/([a-zA-Z ]+)$', 'definitions.views.concept_search'),
    url(r'^$',                    'definitions.views.index'),
)
