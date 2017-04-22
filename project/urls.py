from django.conf import settings
from django.conf.urls import url, include

from main.views import admin, concepts, drafts, main, mathitems, media, sources

user_patterns = [
    url(r'^login$', main.login, name='login'),
    url(r'^logout$', main.logout, name='logout'),
    url(r'^current$', main.current_user),
    url(r'^(\d+)$', main.user_home, name='user-home'),
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

admin_patterns = [
    url(r'^backup', admin.backup, name='admin-backup'),
    url(r'^datadump$', admin.datadump),
]

definitions_patterns = [
    url(r'^$', mathitems.def_home, name='def-home'),
    url(r'^list$', mathitems.def_list, name='def-list'),
    url(r'^search$', mathitems.def_search, name='def-search'),
]

media_patterns = [
    url(r'^$', media.home, name='media-home'),
    url(r'^add$', media.media_add, name='media-add'),
    url(r'^search$', media.media_search, name='media-search'),
]

proofs_patterns = [
    url(r'^$', mathitems.prf_home, name='prf-home'),
    url(r'^list$', mathitems.prf_list, name='prf-list'),
    url(r'^search', mathitems.prf_search, name='prf-search'),
]

theorems_patterns = [
    url(r'^$', mathitems.thm_home, name='thm-home'),
    url(r'^list$', mathitems.thm_list, name='thm-list'),
    url(r'^search$', mathitems.thm_search, name='thm-search'),
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
    url(r'^admin/', include(admin_patterns)),
    url(r'^user/', include(user_patterns)),
    url(r'^concept/([-a-z]+)$', concepts.show_concept, name='concept-page'),
    url(r'^concepts/$', concepts.list_concepts, name='list-concepts'),
    url(r'^definitions/', include(definitions_patterns)),
    url(r'^drafts/', include(drafts_patterns)),
    url(r'^media/', include(media_patterns)),
    url(r'^proofs/', include(proofs_patterns)),
    url(r'^theorems/', include(theorems_patterns)),
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
