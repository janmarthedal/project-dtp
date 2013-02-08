from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^add$', 'items.views.new', { 'kind': 'theorem' }),
    url(r'^$',    'theorems.views.index'),
)


