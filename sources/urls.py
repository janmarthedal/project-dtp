from django.conf.urls import patterns, url

urlpatterns = patterns('sources.views',
    url(r'^$',          'index'),
    url(r'^add/(\w+)$', 'add_source'),
)

