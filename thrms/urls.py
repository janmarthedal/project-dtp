from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^admin/',        include('admin.urls')),
    url(r'^users/',        include('users.urls')),
    url(r'^sources/',      include('refs.urls')),
    url(r'^media/',        include('media.urls')),
    url(r'^item/',         include('items.urls')),
    url(r'^theorems/',     include('items.theorems.urls')),
    url(r'^definitions/',  include('items.definitions.urls')),
    url(r'^proofs/',       include('items.proofs.urls')),
    url(r'^(\w+)$',        'items.views.show_final'),
    url(r'^$',             'main.views.index'),
)

