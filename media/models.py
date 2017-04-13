from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models


class Media(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    format = models.CharField(max_length=32)
    path = models.CharField(max_length=128)

    class Meta:
        db_table = 'media'

    def get_name(self):
        return 'M{}'.format(self.id)

    def get_absolute_url(self):
        return reverse('media-show', args=[self.get_name()])
