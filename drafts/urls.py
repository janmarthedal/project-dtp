from django.conf.urls import patterns, url

urlpatterns = patterns('drafts.views',
    url(r'^(\d+)$',         'show'),
    url(r'^(\d+)/edit$',    'edit'),
    url(r'^(\d+)/delete$',  'delete_draft'),
    url(r'^(\d+)/publish$', 'to_final'),
    url(r'^(\d+)/review$',  'to_review'),
)

urlpatterns += patterns('sources.views',
    url(r'^(\d+)/add-validation/(\d+)$', 'add_location_for_draft'),
)
