from django.db import models

class MathItem(models.Model):
    DEFINITION = 'D'
    THEOREM = 'T'
    PROOF = 'P'
    MATH_ITEM_TYPES = (
        (DEFINITION, 'definition'),
        (THEOREM, 'theorem'),
        (PROOF, 'proof'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    item_type = models.CharField(max_length=1, choices=MATH_ITEM_TYPES, blank=False)
    body = models.TextField(blank=True)

    def __str__(self):
        return '{}-{}'.format(self.item_type, self.id)

class DraftItem(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)
    item_type = models.CharField(max_length=1, choices=MathItem.MATH_ITEM_TYPES, blank=False)
    body = models.TextField(blank=True)

    def __str__(self):
        return 'Draft {}-{}'.format(self.item_type, self.id)
