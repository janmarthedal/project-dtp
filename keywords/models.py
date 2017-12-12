from django.db import models
from django.conf import settings

from mathitems.models import MathItem
from media.models import Media


class Keyword(models.Model):
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        db_table = 'keywords'

    def __str__(self):
        return self.name


class ItemKeyword(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey(MathItem, db_index=True, on_delete=models.CASCADE)
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)

    class Meta:
        db_table = 'item_keyword'
        unique_together = ('item', 'keyword')


class MediaKeyword(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    media = models.ForeignKey(Media, db_index=True, on_delete=models.CASCADE)
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)

    class Meta:
        db_table = 'media_keyword'
        unique_together = ('media', 'keyword')
