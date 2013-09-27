from django.conf.urls import patterns, url

urlpatterns = patterns('api.tags.views',
    url(r'^list$', 'tag_list'),
)
