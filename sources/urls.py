from django.conf.urls import patterns, url

urlpatterns = patterns('sources.views',
    url(r'^list$',                'index'),
    url(r'^add$',                 'add_source'),
    url(r'^add/for-item/(\w+)$',  'add_source_for_item'),
    url(r'^add/for-draft/(\d+)$', 'add_source_for_draft'),
)

