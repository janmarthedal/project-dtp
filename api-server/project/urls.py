from django.conf.urls import url
import main.views

urlpatterns = [
    url(r'^api/drafts/', main.views.drafts),
]
