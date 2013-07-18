from django.conf.urls import patterns, url

urlpatterns = patterns('api.views',
    url(r'^tags/prefixed/(.*)$', 'tags_prefixed'),
    url(r'^items$',              'items'),
    url(r'^drafts$',             'drafts'),
    url(r'^drafts/(\d+)$',       'drafts_id'),
)
