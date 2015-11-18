from django.conf.urls import include, url
import main.views

urlpatterns = [
    url(r'^create$', main.views.create),
]
