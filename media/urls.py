from django.conf.urls import patterns, url

urlpatterns = patterns('media.views',
    url(r'^list$',     'index'),
    url(r'^add$',      'add'),
    url(r'^id/(\w+)$', 'view'),
)
