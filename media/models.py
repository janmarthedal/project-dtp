from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models


"""class MediaManager(models.Manager):
    def get_by_name(self, name):
        if name[0] != 'M':
            raise Media.DoesNotExist()
        return self.get(id=int(name[1:]))"""


class Media(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'media'

    def get_name(self):
        return 'M{}'.format(self.id)

    def get_absolute_url(self):
        return reverse('media-show', args=[self.get_name()])


class SVGImage(models.Model):
    parent = models.ForeignKey(Media, on_delete=models.CASCADE, null=True)
    path = models.CharField(max_length=128)

    class Meta:
        db_table = 'svgimage'


class CindyMedia(models.Model):
    parent = models.ForeignKey(Media, on_delete=models.CASCADE, null=True)
    path = models.CharField(max_length=128)
    version = models.CharField(max_length=16)
    aspect_ratio = models.FloatField()
    data = models.TextField()

    class Meta:
        db_table = 'cindymedia'
