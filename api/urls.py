from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^tags/',     include('api.tags.urls')),
    url(r'^category/', include('api.category.urls')),
    url(r'^draft/',    include('api.draft.urls')),
    url(r'^item/',     include('api.item.urls')),
    url(r'^source/',   include('api.source.urls')),
    url(r'^document/', include('api.document.urls')),
)
