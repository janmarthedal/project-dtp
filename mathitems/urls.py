from django.conf.urls import url

import mathitems.views

urlpatterns = [
    url(r'^([DTP][1-9]\d*)$', mathitems.views.show_item, name='show-item'),
    url(r'^definitions/$', mathitems.views.def_home, name='def-home'),
    url(r'^theorems/$', mathitems.views.thm_home, name='thm-home'),
]
