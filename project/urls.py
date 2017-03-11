from django.conf.urls import url, include

from main.views import admin, concepts, drafts, main, mathitems, sources

accounts_patterns = [
    url(r'^login/$', main.login, name='login'),
    url(r'^logout/$', main.logout, name='logout'),
    url(r'^profile/$', main.profile, name='profile'),
]

drafts_patterns = [
    url(r'^$', drafts.list_drafts, name='list-drafts'),
    url(r'^new/definition$', drafts.new_definition, name='new-def'),
    url(r'^new/theorem$', drafts.new_theorem, name='new-thm'),
    url(r'^new/proof/(T[1-9]\d*)$', drafts.new_proof, name='new-prf'),
    url(r'^(\d+)$', drafts.show_draft, name='show-draft'),
    url(r'^(\d+)/edit$', drafts.edit_draft, name='edit-draft'),
    url(r'^clone/([DTP][1-9]\d*)$', drafts.copy_to_draft, name='copy-to-draft'),
]

urlpatterns = [
    url(r'^$', main.home, name='home'),
    url('', include('social_django.urls', namespace='social')),
    url(r'^([DTP][1-9]\d*)$', mathitems.show_item, name='show-item'),
    url(r'^([DTP][1-9]\d*)/dump$', mathitems.dump_item, name='dump-item'),
    url(r'^([DTP][1-9]\d*)/add-validation$', mathitems.add_item_validation, name='add-item-validation'),
    url(r'^definitions/$', mathitems.def_home, name='def-home'),
    url(r'^theorems/$', mathitems.thm_home, name='thm-home'),
    url(r'^proofs/$', mathitems.prf_home, name='prf-home'),
    url(r'^accounts/', include(accounts_patterns)),
    url(r'^drafts/', include(drafts_patterns)),
    url(r'^datadump$', admin.datadump),
    url(r'^sources/$', sources.sources_list, name='sources-list'),
    url(r'^concept/([-a-z]+)$', concepts.show_concept),
]
