from django.conf.urls import url, include

import main.views
import drafts.views

urlpatterns = [
    url('', include('social.apps.django_app.urls', namespace='social')),
    url('', include('mathitems.urls')),
    url(r'^$', main.views.home, name='home'),
    url(r'^accounts/login/$', main.views.login, name='login'),
    url(r'^accounts/logout/$', main.views.logout, name='logout'),
    url(r'^accounts/profile/$', main.views.profile, name='profile'),
    url(r'^drafts/def/new$', drafts.views.new_definition, name='new-def'),
    url(r'^drafts/thm/new$', drafts.views.new_theorem, name='new-thm'),
    url(r'^drafts/', include('drafts.urls')),
]
