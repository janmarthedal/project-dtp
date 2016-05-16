from django.conf.urls import url

import main.views

urlpatterns = [
    url(r'^test-eqn$', main.views.test_eqn),
    url(r'^test-item-prep$', main.views.test_item_prep),
]
