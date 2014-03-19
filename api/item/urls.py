from django.conf.urls import patterns, url

urlpatterns = patterns('api.item.views',
    url(r'^(\w+)$', 'final_id'),
    url(r'^(\w+)/validation-vote$', 'validation_vote'),
)
