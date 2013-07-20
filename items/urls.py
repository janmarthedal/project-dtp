from django.conf.urls import patterns, url

urlpatterns = patterns('items.views',
    url(r'^delete_public$',    'delete_public'),
    url(r'^(\d+)$',            'show'),
    url(r'^(\d+)/edit$',       'edit'),
    url(r'^(\d+)/delete$',     'delete_draft'),
    url(r'^(\d+)/set_status$', 'change_status'),
)
