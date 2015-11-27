from django.db import models

class Concept(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=64)

class MathItem(models.Model):
    DEFINITION = 'D'
    THEOREM = 'T'
    PROOF = 'P'
    MATH_ITEM_TYPES = (
        (DEFINITION, 'Definition'),
        (THEOREM, 'Theorem'),
        (PROOF, 'Proof'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)
    item_type = models.CharField(max_length=1, choices=MATH_ITEM_TYPES)
    body = models.TextField(blank=True)
    concepts_defined = models.ManyToManyField(Concept, related_name='+')
    concepts_referenced = models.ManyToManyField(Concept, related_name='+')
    items_referenced = models.ManyToManyField('self', through='ItemReference', symmetrical=False)

class ItemReference(models.Model):
    from_mathitem = models.ForeignKey(MathItem, related_name='+')
    to_mathitem = models.ForeignKey(MathItem, related_name='+')
    concept = models.ForeignKey(Concept, null=True)
