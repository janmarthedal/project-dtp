from django.conf.urls import patterns, url

urlpatterns = patterns('api.source.views',
    url(r'^$',       'source'),
    url(r'^search$', 'source_search'),
)
