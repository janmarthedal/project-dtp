from django.conf.urls import url

import admin.views

urlpatterns = [
    url(r'^datadump$', admin.views.datadump),
]
