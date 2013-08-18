from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^browserid/',    include('django_browserid.urls')),
    url(r'^api/',          include('api.urls')),
    url(r'^users/',        include('users.urls')),
    url(r'^sources/',      include('sources.urls')),
    url(r'^media/',        include('media.urls')),
    url(r'^draft/',        include('drafts.urls')),
    url(r'^item/',         include('items.urls')),
    url(r'^theorems/',     include('items.theorems.urls')),
    url(r'^definitions/',  include('items.definitions.urls')),
    url(r'^proofs/',       include('items.proofs.urls')),
    url(r'^categories/',   include('tags.urls')),
    url(r'^about$',        'main.views.about'),
    url(r'^$',             'main.views.index'),
)
