from django.conf import settings
from django.conf.urls import url, include

from main.views import admin, concepts, drafts, main, mathitems, media, sources

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
    url(r'^([DTP][1-9]\d*)/keywords$', mathitems.edit_item_keywords, name='edit-item-keywords'),
    url(r'^(M[1-9]\d*)$', media.show_media, name='media-show'),
    url(r'^(M[1-9]\d*)/keywords$', media.edit_media_keywords, name='edit-media-keywords'),
    url(r'^admin/backup', admin.backup),
    url(r'^admin/datadump$', admin.datadump),
    url(r'^accounts/', include(accounts_patterns)),
    url(r'^concept/([-a-z]+)$', concepts.show_concept, name='concept-page'),
    url(r'^concepts/$', concepts.list_concepts, name='list-concepts'),
    url(r'^definitions/$', mathitems.def_home, name='def-home'),
    url(r'^definitions/list$', mathitems.def_list, name='def-list'),
    url(r'^definitions/search$', mathitems.def_search, name='def-search'),
    url(r'^drafts/', include(drafts_patterns)),
    url(r'^media/$', media.home, name='media-home'),
    url(r'^media/add$', media.media_add, name='media-add'),
    url(r'^proofs/$', mathitems.prf_home, name='prf-home'),
    url(r'^proofs/list$', mathitems.prf_list, name='prf-list'),
    url(r'^proofs/search', mathitems.prf_search, name='prf-search'),
    url(r'^theorems/$', mathitems.thm_home, name='thm-home'),
    url(r'^theorems/list$', mathitems.thm_list, name='thm-list'),
    url(r'^theorems/search$', mathitems.thm_search, name='thm-search'),
    url(r'^sources/$', sources.sources_list, name='sources-list'),
]

if settings.DEBUG:
    from os.path import join
    from django.conf.urls.static import static
    from django.views.static import serve

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        url(r'^(?P<path>favicon.ico)$', serve, {
            'document_root': join(settings.BASE_DIR, 'main', 'static', 'main')
        })
    ]
