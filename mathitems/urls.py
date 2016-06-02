from django.conf.urls import url

import mathitems.views

urlpatterns = [
    url(r'^D([1-9]\d*)$', mathitems.views.show_def, name='show-def'),
    url(r'^T([1-9]\d*)$', mathitems.views.show_thm, name='show-thm'),
]
