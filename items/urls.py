from django.conf.urls import patterns, include, url

urlpatterns = patterns('items.views',
    url(r'^theorem/new$',    'new_theorem',    name='new_theorem_view'),
    url(r'^definition/new$', 'new_definition', name='new_definition_view'),
)

