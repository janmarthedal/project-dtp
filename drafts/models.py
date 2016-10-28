from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.utils import IntegrityError
from django.utils import timezone

from mathitems.models import Equation, ItemTypes, MathItem
from project.server_com import prepare_item, render_eqns

#import logging
#logger = logging.getLogger(__name__)


class DraftItem(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    item_type = models.CharField(max_length=1, choices=ItemTypes.CHOICES)
    parent = models.ForeignKey(MathItem, null=True, blank=True)
    body = models.TextField(blank=True)

    class Meta:
        db_table = 'drafts'

    def __str__(self):
        return '{} (Draft{})'.format(self.get_item_type_display(),
                                     ' {}'.format(self.id) if self.id else '')

    def clean(self):
        if self.item_type == ItemTypes.PRF:
            if not self.parent or self.parent.item_type != ItemTypes.THM:
                raise ValidationError('A Proof must have a Theorem parent')
        elif self.parent:
            raise ValidationError('A {} may not have a parent'.format(self.get_item_type_display()))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('show-draft', args=[self.id])

    def prepare(self):
        body = self.body.strip()
        document, eqns = prepare_item(body)
        rendered_eqns = {}

        to_render = {}
        for key, data in eqns.items():
            try:
                eqn = Equation.objects.get(format=data['format'], math=data['math'])
                if eqn.draft_access_at:  # cached draft equation?
                    eqn.draft_access_at = timezone.now()
                    eqn.save()
                rendered_eqns[key] = eqn.to_data()
            except Equation.DoesNotExist:
                to_render[key] = data

        new_rendered_eqns = render_eqns(to_render)
        for key, data in new_rendered_eqns.items():
            try:
                eqn = Equation.objects.create(format=data['format'], math=data['math'], html=data['html'])
            except IntegrityError:
                # equation was created in the meantime by another thread
                # TODO: Is this even possible? protected by transaction?
                eqn = Equation.objects.get(format=data['format'], math=data['math'])
            rendered_eqns[key] = eqn.to_data()

        return document, rendered_eqns
