from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from password_rotate.models import PasswordHistory


class NotPreviousPasswordValidator:
    """
    Validate that the password is not a previously used password.

    The password is rejected if it exists in `PasswordHistory`.
    """

    def validate(self, password, user=None):
        """
        Return True when the password has not been stored in `PasswordHistory`
        """
        if not PasswordHistory.objects.check_password(user, password):
            raise ValidationError("You already used this password.")
        else:
            # This flag allows to store the password in `PasswordHistory`
            # when `set_password` is called
            user._has_not_previous_password = True
            return True

    def get_help_text(self):
        return _("Your password must be different from any previous one.")
