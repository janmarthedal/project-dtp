from django.conf.urls import url

import drafts.views

urlpatterns = [
    url(r'^$', drafts.views.list_drafts, name='list-drafts'),
    url(r'^new/definition$', drafts.views.new_definition, name='new-def'),
    url(r'^new/theorem$', drafts.views.new_theorem, name='new-thm'),
    url(r'^(\d+)$', drafts.views.show_draft, name='show-draft'),
    url(r'^(\d+)/edit$', drafts.views.edit_draft, name='edit-draft'),
]
