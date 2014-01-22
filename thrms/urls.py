from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^api/',         include('api.urls')),
    url(r'^user/',        include('users.urls')),
    url(r'^source/',      include('sources.urls')),
    url(r'^media/',       include('media.urls')),
    url(r'^draft/',       include('drafts.urls')),
    url(r'^item/',        include('items.urls')),
    url(r'^theorems/',    include('items.theorems.urls')),
    url(r'^definitions/', include('items.definitions.urls')),
    url(r'^proofs/',      include('items.proofs.urls')),
    url(r'^category/',    include('tags.urls')),
    url(r'^document/',    include('document.urls')),
    url(r'^about$',       'main.views.about'),
    url(r'^$',            'main.views.index'),
    url(r'^auth/',        include('social.apps.django_app.urls', namespace='social')),
)
