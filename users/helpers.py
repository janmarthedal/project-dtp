import six
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from social.exceptions import SocialAuthBaseException
from users.models import Invitations

class AuthMissingInvitation(SocialAuthBaseException):
    def __str__(self):
        return 'Missing invitation'

class AuthIllegalInvitation(SocialAuthBaseException):
    def __str__(self):
        return 'Illegal invitation token'

# social auth middleware
class CustomSocialAuthExceptionMiddleware(object):
    def process_exception(self, request, exception):
        strategy = getattr(request, 'social_strategy', None)
        if strategy is None:
            return
        if isinstance(exception, SocialAuthBaseException):
            messages.error(request, six.text_type(exception))
            return redirect(reverse('users.views.login'))

# social auth pipeline
def check_new_user(request, user=None, *args, **kwargs):
    if user:
        return
    if 'invite_token' not in request.session:
        raise AuthMissingInvitation()
    token = request.session['invite_token']
    try:
        invite = Invitations.objects.get(token=token)
        invite.delete()
    except Invitations.DoesNotExist:
        raise AuthIllegalInvitation()
