from django.conf.urls import patterns, include, url

urlpatterns = patterns('items.views',
    url(r'^theorem/new$',    'new_theorem'),
    url(r'^definition/new$', 'new_definition'),
    url(r'^edit$',           'edit'),
)

