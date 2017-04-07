from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from userdata.models import UserData

import logging
logger = logging.getLogger(__name__)


def user_saved(sender, instance, created, **kwargs):
    if created:
        logger.info('New user: {}'.format(instance.username))
        UserData.objects.new_user(instance)


post_save.connect(user_saved, sender=get_user_model(), dispatch_uid='user-saved-signal')
