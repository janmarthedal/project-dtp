from django.conf.urls import patterns, url

urlpatterns = patterns('users.views',
    url(r'^login$',               'login'),
    url(r'^logout$',              'logout'),
    url(r'^profile/(\d+)/items$', 'items'),
    url(r'^profile/(\d+)$',       'profile'),
    url(r'^$',                    'index'),
)

