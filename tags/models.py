from django.db import models
from tags.helpers import normalize_tag

import logging
logger = logging.getLogger(__name__)


class TagManager(models.Manager):

    def fetch(self, name):
        normalized = normalize_tag(name)
        tag, created = self.get_or_create(name=name,
                                          defaults={'normalized':normalized})
        return tag


class Tag(models.Model):
    
    class Meta:
        db_table = 'tags'
    
    objects = TagManager()

    name       = models.CharField(max_length=255, db_index=True, unique=True)
    normalized = models.CharField(max_length=255, db_index=True, unique=False)
    
    def __unicode__(self):
        return self.name


