from django.conf.urls import url

import main.views

urlpatterns = [
    url(r'^new-item$', main.views.new_item),
]
