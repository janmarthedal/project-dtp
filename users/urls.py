from django.conf.urls import patterns, include, url

urlpatterns = patterns('users.views',
    url(r'^login$',   'login',   name='login_view'),
    url(r'^logout$',  'logout',  name='logout_view'),
    url(r'^account$', 'account', name='account_view'),
)

