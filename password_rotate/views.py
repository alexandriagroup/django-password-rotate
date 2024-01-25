from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import PasswordChangeView


class ForcePasswordChangeView(PasswordChangeView):
    def form_valid(self, form):
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one.
        update_session_auth_hash(self.request, form.user)
        self.request.password_status = "valid"
        return super().form_valid(form)
