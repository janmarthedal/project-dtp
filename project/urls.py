from django.conf.urls import include, url
from django.contrib import admin
import main.views

urlpatterns = [
    url(r'^create$', main.views.create),
    url(r'^admin/', include(admin.site.urls)),
]
