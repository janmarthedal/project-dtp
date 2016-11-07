from django.conf.urls import url, include

from main.views import (
    admin as admin_views,
    drafts as drafts_views,
    main as main_views,
    mathitems as mathitems_views,
    sources as sources_views,
)

accounts_patterns = [
    url(r'^login/$', main_views.login, name='login'),
    url(r'^logout/$', main_views.logout, name='logout'),
    url(r'^profile/$', main_views.profile, name='profile'),
]

drafts_patterns = [
    url(r'^$', drafts_views.list_drafts, name='list-drafts'),
    url(r'^new/definition$', drafts_views.new_definition, name='new-def'),
    url(r'^new/theorem$', drafts_views.new_theorem, name='new-thm'),
    url(r'^new/proof/(T[1-9]\d*)$', drafts_views.new_proof, name='new-prf'),
    url(r'^(\d+)$', drafts_views.show_draft, name='show-draft'),
    url(r'^(\d+)/edit$', drafts_views.edit_draft, name='edit-draft'),
    url(r'^clone/([DTP][1-9]\d*)$', drafts_views.copy_to_draft, name='copy-to-draft'),
]

urlpatterns = [
    url(r'^$', main_views.home, name='home'),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^([DTP][1-9]\d*)$', mathitems_views.show_item, name='show-item'),
    url(r'^([DTP][1-9]\d*)/dump$', mathitems_views.dump_item, name='dump-item'),
    url(r'^([DTP][1-9]\d*)/add-validation$', mathitems_views.add_item_validation, name='add-item-validation'),
    url(r'^definitions/$', mathitems_views.def_home, name='def-home'),
    url(r'^theorems/$', mathitems_views.thm_home, name='thm-home'),
    url(r'^proofs/$', mathitems_views.prf_home, name='prf-home'),
    url(r'^accounts/', include(accounts_patterns)),
    url(r'^drafts/', include(drafts_patterns)),
    url(r'^datadump$', admin_views.datadump),
    url(r'^sources/$', sources_views.sources_list),
]
