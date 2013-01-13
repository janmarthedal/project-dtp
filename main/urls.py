from django.conf.urls import patterns, include, url

urlpatterns = patterns('main.views',
                       url(r'^$',             'index'),
                       url(r'^user/login$',   'user_login', name='login_view'),
                       url(r'^user/account$', 'user_account'),
                       #url(r'^(?P<item_id>.+)$', 'show_item')
                       )

