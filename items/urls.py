from django.conf.urls import patterns, url

urlpatterns = patterns('items.views',
    url(r'^(\w+)$',        'show_final'),
    url(r'^(\w+)/edit$',   'edit_final'),
    url(r'^(\w+)/delete$', 'delete_final'),
)
