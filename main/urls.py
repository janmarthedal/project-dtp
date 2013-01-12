from django.conf.urls import patterns, include, url

urlpatterns = patterns('main.views',
                       url(r'^$',                'index'),
                       #url(r'^(?P<item_id>.+)$', 'show_item')
                       )

