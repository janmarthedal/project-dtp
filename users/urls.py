from django.conf.urls import patterns, url

urlpatterns = patterns('users.views',
    url(r'^login$',         'login'),
    url(r'^closed-beta$',   'closed_beta'),
    url(r'^current$',       'profile_current'),
    url(r'^profile/(\d+)$', 'profile'),
    url(r'^list$',          'index'),
)

