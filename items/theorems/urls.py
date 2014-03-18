from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^add$', 'drafts.views.new', {'kind': 'theorem'}),
    url(r'^named/(.*)$', 'tags.views.theorems_in_category'),
    url(r'^$', 'items.theorems.views.index'),
)
