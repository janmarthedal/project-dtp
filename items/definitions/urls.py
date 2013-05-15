from django.conf.urls import patterns, url

urlpatterns = patterns('items',
    url(r'^add$', 'views.new', { 'kind': 'definition' }),
    url(r'^$',    'definitions.views.index'),
)

