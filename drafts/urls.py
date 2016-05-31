from django.conf.urls import url

import drafts.views

urlpatterns = [
    url(r'^(\d+)$', drafts.views.show_draft, name='show-draft'),
    url(r'^(\d+)/edit$', drafts.views.edit_draft, name='edit-draft'),
]
