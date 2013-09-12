from django.conf.urls import patterns, url

urlpatterns = patterns('api.views',
    url(r'^tags/prefixed/(.*)$', 'tags_prefixed'),
    url(r'^draft/$',             'drafts'),
    url(r'^draft/(\d+)$',        'drafts_id'),
    url(r'^item/search$',        'items'),
    url(r'^item/(\w+)$',         'final_id'),
    url(r'^source/$',            'source'),
    url(r'^source/search$',      'source_search'),
)
