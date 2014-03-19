from django.conf.urls import patterns, url

urlpatterns = patterns('api.draft.views',
    url(r'^$', 'drafts'),
    url(r'^(\d+)$', 'drafts_id'),
)
