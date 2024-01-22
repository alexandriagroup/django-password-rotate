from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, user_logged_in
from django.db.models import signals
from django.utils import timezone

from .models import PasswordChange
from .utils import PasswordChecker


def create_user_handler(sender, instance, created, **kwargs):
    # when the user is created, set the password last changed field to now
    if created:
        now = timezone.now()
        PasswordChange.objects.create(user=instance, last_changed=now)


def change_password_handler(sender, instance, **kwargs):
    # Checks if the user changed password
    # contrib/auth/base_user.py sets _password in set_password()
    if instance._password is None:
        return

    try:
        get_user_model().objects.get(id=instance.id)
    except get_user_model().DoesNotExist:
        return

    record, _ = PasswordChange.objects.get_or_create(user=instance)
    record.last_changed = timezone.now()
    record.save()


def login_handler(sender, request, user, **kwargs):
    checker = PasswordChecker(request.user)
    if checker.is_expired():
        # Login with expired password then redirect to change the password.
        # This solution is faster and probably as safe as resetting the password
        # by sending a token the user by email.
        messages.error(request, "Password expired. You have to change your password.")

        # set flag for middleware to pick up
        request.redirect_to_password_change = True


def register_signals():
    signals.post_save.connect(
        create_user_handler,
        sender=settings.AUTH_USER_MODEL,
        dispatch_uid="password_rotate:create_user_handler",
    )

    signals.pre_save.connect(
        change_password_handler,
        sender=settings.AUTH_USER_MODEL,
        dispatch_uid="password_rotate:change_password_handler",
    )

    user_logged_in.connect(
        login_handler,
        dispatch_uid="password_rotate:login_handler"
    )
