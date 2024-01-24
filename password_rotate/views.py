from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import PasswordChangeView


class ForcePasswordChangeView(PasswordChangeView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        self.request.password_changed = None
        return kwargs

    def form_valid(self, form):
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one.
        update_session_auth_hash(self.request, form.user)
        self.request.password_status = "valid"
        print("password_changed set to True")
        return super().form_valid(form)
