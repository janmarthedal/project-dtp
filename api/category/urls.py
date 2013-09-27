from django.conf.urls import patterns, url

urlpatterns = patterns('api.category.views',
    url(r'^list/(.*)$', 'list_sub_categories'),
)
