from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^add$', 'items.views.new', { 'kind': 'definition' }),
    url(r'^$',    'definitions.views.index' ),
)


