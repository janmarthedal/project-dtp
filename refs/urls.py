from django.conf.urls import patterns, url

urlpatterns = patterns('refs.views',
    url(r'^$',          'index'),
    url(r'^add/(\w+)$', 'add_source'),
)

