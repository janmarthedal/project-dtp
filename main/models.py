from django.core.urlresolvers import reverse
from django.db import models

class Equation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    body = models.TextField(blank=True)

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

    def get_slug(self):
        return '{}{:04}'.format(self.item_type, self.id)

    def get_title(self):
        return '{} {}'.format(self.get_item_type_display().capitalize(), self.get_slug())

    #def get_absolute_url(self):
    #    return reverse('view-item', args=[self.get_slug()])

    def __str__(self):
        return self.get_title()

class DraftItem(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)
    item_type = models.CharField(max_length=1, choices=MathItem.MATH_ITEM_TYPES, blank=False)
    body = models.TextField(blank=True)

    def get_slug(self):
        return str(self.id)

    def get_title(self):
        return 'Draft {} {}'.format(self.get_item_type_display().capitalize(), self.get_slug())

    def get_absolute_url(self):
        return reverse('view-draft', args=[self.get_slug()])

    def __str__(self):
        return self.get_title()
