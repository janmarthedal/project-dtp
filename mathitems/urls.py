from django.conf.urls import url

import mathitems.views

urlpatterns = [
    url(r'^def/(\d+)$', mathitems.views.show_def, name='show-def'),
    url(r'^thm/(\d+)$', mathitems.views.show_thm, name='show-thm'),
]
