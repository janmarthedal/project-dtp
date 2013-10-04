from django.conf.urls import patterns, url

urlpatterns = patterns('api.media.views',
    url(r'^getlinks$', 'get_links'),
)
