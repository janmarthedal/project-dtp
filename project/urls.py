from django.conf.urls import url, include

import main.views

urlpatterns = [
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^$', main.views.home, name='home'),
    url(r'^accounts/login/$', main.views.login, name='login'),
    url(r'^accounts/logout/$', main.views.logout, name='logout'),
    url(r'^accounts/profile/$', main.views.profile, name='profile'),
    url(r'^definitions/new$', main.views.new_definition, name='new-def'),
    url(r'^theorems/new$', main.views.new_theorem, name='new-thm'),
]