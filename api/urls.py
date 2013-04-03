from django.conf.urls import patterns, url

urlpatterns = patterns('api.views',
    url(r'^tags/prefixed/(.*)$', 'tags_prefixed'),
)
