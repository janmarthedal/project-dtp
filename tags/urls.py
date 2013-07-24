from django.conf.urls import patterns, url

urlpatterns = patterns('tags.views',
    url(r'^root/(.*)$', 'show'),
    url(r'^$',          'index'),
)
