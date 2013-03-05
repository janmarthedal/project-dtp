from django.conf.urls import patterns, url

urlpatterns = patterns('media.views',
    url(r'^$',    'index'),
    url(r'^add$', 'add'),
)

