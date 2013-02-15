from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^admin/',        include('admin.urls')),
    url(r'^user/',         include('users.urls')),
    url(r'^item/',         include('items.urls')),
    url(r'^theorems/',     include('theorems.urls')),
    url(r'^definitions/',  include('definitions.urls')),
    url(r'^proofs/',       include('proofs.urls')),
    url(r'^(\w+)$',        'items.views.show_final'),
    url(r'^$',             'main.views.index'),
)

