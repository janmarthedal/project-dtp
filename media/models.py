import json
import os
from shutil import move

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.template.loader import render_to_string


class MediaManager(models.Manager):
    def get_by_name(self, name):
        if name[0] != 'M':
            raise Media.DoesNotExist()
        return self.get(id=int(name[1:]))


class Media(models.Model):
    objects = MediaManager()

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'media'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._main_image = None

    def get_name(self):
        return 'M{}'.format(self.id)

    def get_absolute_url(self):
        return reverse('media-show', args=[self.get_name()])

    def _get_main_image(self):
        if not self._main_image:
            images = self.svgimage_set.all()
            if images:
                self._main_image = images[0]
            else:
                images = self.cindymedia_set.all()
                if images:
                    self._main_image = images[0]
        return self._main_image

    def get_html(self):
        return self._get_main_image().get_html()

    def get_description(self):
        return self._get_main_image().get_description()


class SVGImage(models.Model):
    REFNAME = 'svg'

    parent = models.ForeignKey(Media, on_delete=models.CASCADE, null=True)
    path = models.CharField(max_length=128)

    class Meta:
        db_table = 'svgimage'

    def get_html(self):
        return '<img src="{}">'.format(settings.MEDIA_URL + self.path)

    def get_ref(self):
        return '{}:{}'.format(self.REFNAME, self.pk)

    def get_description(self):
        return 'SVG image'

    def finalize(self, media):
        new_path = '{}.{}'.format(media.get_name(), 'svg')
        move(os.path.join(settings.MEDIA_ROOT, self.path),
             os.path.join(settings.MEDIA_ROOT, new_path))
        self.parent = media
        self.path = new_path
        self.save()


class CindyMedia(models.Model):
    parent = models.ForeignKey(Media, on_delete=models.CASCADE, null=True)
    path = models.CharField(max_length=128)
    version = models.CharField(max_length=16)
    aspect_ratio = models.FloatField()
    data = models.TextField()

    class Meta:
        db_table = 'cindymedia'

    def create_file(self):
        data = json.loads(self.data).get('create', {})
        if 'ports' not in data:
            raise Exception('No ports declaration')
        if type(data['ports']) is not list or len(data['ports']) != 1:
            raise Exception('Illegal ports declaration')
        for key in ['width', 'height']:
            if key in data['ports'][0]:
                del data['ports'][0][key]
        data['ports'][0]['id'] = 'cscanvas'
        data['ports'][0]['fill'] = 'window'
        if 'scripts' in data:
            del data['scripts']

        content = render_to_string('media/cindy-media.html', {
            'lib': 'https://rawgit.com/janmarthedal/CindyJS-builds/master/v{}/Cindy.js'.format(self.version),
            'create': '{{\n{}\n}}'.format(',\n'.join('  "{}": {}'.format(k, json.dumps(v)) for k, v in data.items()))
        })
        with open(os.path.join(settings.MEDIA_ROOT, self.path), 'w') as dst:
            dst.write(content)

    def get_html(self):
        return '''<div style="position: relative; width: 100%; height: 0; padding-bottom: {}%;">
      <iframe style="position: absolute; width: 100%; height: 100%; left: 0; top: 0;" src="{}"></iframe>
</div>'''.format(self.aspect_ratio, settings.MEDIA_URL + self.path)

    def get_description(self):
        return 'CindyJS illustration'

    def finalize(self, media):
        new_path = '{}.{}'.format(media.get_name(), 'html')
        move(os.path.join(settings.MEDIA_ROOT, self.path),
             os.path.join(settings.MEDIA_ROOT, new_path))
        self.parent = media
        self.path = new_path
        self.save()
