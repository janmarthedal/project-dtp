from django.conf.urls import patterns, url

urlpatterns = patterns('items.views',
    url(r'^edit/(\d+)$',    'edit'),
    url(r'^change_status$', 'change_status'),
    url(r'^delete_public$', 'delete_public'),
    url(r'^delete_draft$',  'delete_draft'),
    url(r'^(\d+)$',         'show'),
)
