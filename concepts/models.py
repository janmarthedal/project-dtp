from django.db import models

from mathitems.models import MathItem


class Concept(models.Model):
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        db_table = 'concepts'

    def __str__(self):
        return self.name


class ConceptDefinition(models.Model):
    item = models.ForeignKey(MathItem, db_index=True)
    concept = models.ForeignKey(Concept, db_index=True)

    class Meta:
        db_table = 'concept_defs'
