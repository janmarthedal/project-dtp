from django.conf.urls import patterns, include, url

urlpatterns = patterns('items.views',
    url(r'^edit/(\d+)$',    'edit'),
    url(r'^change_status$', 'change_status'),
    url(r'^(\d+)$',         'show'),
)

urlpatterns += patterns('validate.views',
    url(r'^add/source/(\w+)$', 'add_source'),
)

