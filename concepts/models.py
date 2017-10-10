from django.core.urlresolvers import reverse
from django.db import models

from mathitems.models import MathItem


class Concept(models.Model):
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        db_table = 'concepts'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('concept-page', args=[self.name])


class ConceptDefinition(models.Model):
    item = models.ForeignKey(MathItem, db_index=True)
    concept = models.ForeignKey(Concept, db_index=True)

    class Meta:
        db_table = 'concept_defs'
        unique_together = ('item', 'concept')


class ConceptReference(models.Model):
    item = models.ForeignKey(MathItem, db_index=True)
    concept = models.ForeignKey(Concept, db_index=True)

    class Meta:
        db_table = 'concept_refs'
        unique_together = ('item', 'concept')


class ItemDependency(models.Model):
    item = models.ForeignKey(MathItem, related_name='itemdep_item')
    uses = models.ForeignKey(MathItem, related_name='+')
    concepts = models.ManyToManyField(Concept)  # only when uses.item_type = 'D'

    class Meta:
        db_table = 'item_deps'
        unique_together = ('item', 'uses')

    def __str__(self):
        return '{} -> {}'.format(self.item.get_name(), self.uses.get_name())


class ConceptMeta(models.Model):
    concept = models.OneToOneField(Concept)
    ref_count = models.IntegerField()
    def_count = models.IntegerField()

    class Meta:
        db_table = 'concept_meta'

    def __str__(self):
        return '{} (ref {} def {})'.format(self.id, self.ref_count, self.def_count)
