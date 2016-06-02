from django.conf.urls import url, include

import main.views
import drafts.views

accounts_patterns = [
    url(r'^login/$', main.views.login, name='login'),
    url(r'^logout/$', main.views.logout, name='logout'),
    url(r'^profile/$', main.views.profile, name='profile'),
]

urlpatterns = [
    url(r'^$', main.views.home, name='home'),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url('', include('mathitems.urls')),
    url(r'^accounts/', include(accounts_patterns)),
    url(r'^drafts/', include('drafts.urls')),
    url(r'^definitions/$', main.views.def_home, name='def-home'),
    url(r'^theorems/$', main.views.thm_home, name='thm-home'),
]
