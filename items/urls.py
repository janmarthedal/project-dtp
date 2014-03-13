from django.conf.urls import patterns, url

urlpatterns = patterns('items.views',
    url(r'^search$', 'search'),
    url(r'^(\w+)$', 'show_final'),
    url(r'^(\w+)/edit$', 'edit_final'),
    url(r'^(\w+)/delete$', 'delete_final'),
)

urlpatterns += patterns('sources.views',
    url(r'^(\w+)/add-validation/(\d+)$', 'add_location_for_item'),
)
