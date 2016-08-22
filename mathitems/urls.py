from django.conf.urls import url

import mathitems.views

urlpatterns = [
    url(r'^([DTP][1-9]\d*)$', mathitems.views.show_item, name='show-item'),
    url(r'^([DTP][1-9]\d*)/add-validation$', mathitems.views.add_item_validation, name='add-item-validation'),
    url(r'^definitions/$', mathitems.views.def_home, name='def-home'),
    url(r'^theorems/$', mathitems.views.thm_home, name='thm-home'),
    url(r'^proofs/$', mathitems.views.prf_home, name='prf-home'),
]
