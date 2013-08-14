from django.conf.urls import patterns, url

urlpatterns = patterns('users.views',
    url(r'^login$',         'login'),
    url(r'^current$',       'profile_current'),
    url(r'^profile/(\d+)$', 'profile'),
    url(r'^$',              'index'),
)

