from django.conf import settings
from django.db import models

class DraftItem(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    body = models.TextField(blank=True)
