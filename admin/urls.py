from django.conf.urls import patterns, url

urlpatterns = patterns('admin.views',
    url(r'^$',            'index'),
    url(r'^recalc-deps$', 'recalc_deps'),
)

