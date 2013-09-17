from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^add$',  'drafts.views.new', { 'kind': 'theorem' }),
    url(r'^list$', 'items.theorems.views.index'),
)
