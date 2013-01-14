from django.conf.urls import patterns, include, url

urlpatterns = patterns('users.views',
    url(r'^login$',   'login'),
    url(r'^logout$',  'logout'),
    url(r'^account$', 'account'),
)

