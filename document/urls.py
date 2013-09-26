from django.conf.urls import patterns, url

urlpatterns = patterns('document.views',
    url(r'^id/(\d+)$', 'view'),
    url(r'^delete$',   'delete'),
)
