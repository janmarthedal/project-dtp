from django.conf.urls import patterns, url

urlpatterns = patterns('sources.views',
    url(r'^$',                   'index'),
    url(r'^add$',                'add_source'),
    url(r'^add/for-item/(\w+)$', 'add_source_for_item'),
)

