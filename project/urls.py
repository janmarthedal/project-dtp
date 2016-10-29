from django.conf.urls import url, include

import admin.views
import drafts.views
import main.views
import mathitems.views

accounts_patterns = [
    url(r'^login/$', main.views.login, name='login'),
    url(r'^logout/$', main.views.logout, name='logout'),
    url(r'^profile/$', main.views.profile, name='profile'),
]

drafts_patterns = [
    url(r'^$', drafts.views.list_drafts, name='list-drafts'),
    url(r'^new/definition$', drafts.views.new_definition, name='new-def'),
    url(r'^new/theorem$', drafts.views.new_theorem, name='new-thm'),
    url(r'^new/proof/(T[1-9]\d*)$', drafts.views.new_proof, name='new-prf'),
    url(r'^(\d+)$', drafts.views.show_draft, name='show-draft'),
    url(r'^(\d+)/edit$', drafts.views.edit_draft, name='edit-draft'),
]

urlpatterns = [
    url(r'^$', main.views.home, name='home'),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^([DTP][1-9]\d*)$', mathitems.views.show_item, name='show-item'),
    url(r'^([DTP][1-9]\d*)/add-validation$', mathitems.views.add_item_validation, name='add-item-validation'),
    url(r'^definitions/$', mathitems.views.def_home, name='def-home'),
    url(r'^theorems/$', mathitems.views.thm_home, name='thm-home'),
    url(r'^proofs/$', mathitems.views.prf_home, name='prf-home'),
    url(r'^accounts/', include(accounts_patterns)),
    url(r'^drafts/', include(drafts_patterns)),
    url(r'^datadump$', admin.views.datadump),
]
