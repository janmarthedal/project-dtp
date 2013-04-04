from django.conf.urls import patterns, url

urlpatterns = patterns('items',
    url(r'^add$',    'views.new', { 'kind': 'theorem' }),
    url(r'^search$', 'theorems.views.search'),
    url(r'^$',       'theorems.views.index'),
)


