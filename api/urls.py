from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^tags/prefixed/(.*)$', 'api.views.tags_prefixed'),
    url(r'^draft/$',             'api.views.drafts'),
    url(r'^draft/(\d+)$',        'api.views.drafts_id'),
    url(r'^item/search$',        'api.views.items'),
    url(r'^item/(\w+)$',         'api.views.final_id'),
    url(r'^source/$',            'api.views.source'),
    url(r'^source/search$',      'api.views.source_search'),
    url(r'^document/',           include('api.document.urls')),
)
