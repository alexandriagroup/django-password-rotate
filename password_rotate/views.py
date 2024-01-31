from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import PasswordChangeView

from password_rotate.forms import ForcePasswordChangeForm


class ForcePasswordChangeView(PasswordChangeView):
    """
    This view forces the user to change her password when it expired.

    Updating the password properly will change the password status from "expired"
    to "valid".
    """
    form_class = ForcePasswordChangeForm

    def form_valid(self, form):
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one.
        update_session_auth_hash(self.request, form.user)
        self.request.password_status = "valid"
        return super().form_valid(form)
