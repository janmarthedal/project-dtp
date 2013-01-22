from django.db import models

class RefField(models.Model):
    class Meta:
        db_table = 'ref_field'
    name = models.CharField(max_length=32)

class RefAttribute(models.Model):
    class Meta:
        db_table = 'ref_attribute'
    field = models.ForeignKey(RefField)
    value = models.CharField(max_length=128)

class RefNode(models.Model):
    class Meta:
        db_table = 'ref_node'
    attributes = models.ManyToManyField(RefAttribute)

