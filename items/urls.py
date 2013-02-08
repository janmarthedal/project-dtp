from django.conf.urls import patterns, include, url

urlpatterns = patterns('items.views',
    url(r'^show/(\d+)$',                'show'),
    url(r'^edit/(\d+)$',                'edit'),
    url(r'^change_status$',             'change_status'),
)

urlpatterns += patterns('validate.views',
    url(r'^add/source/(\w+)$', 'add_source'),
)

