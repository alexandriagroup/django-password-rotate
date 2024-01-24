from django.contrib import messages
from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.utils.safestring import mark_safe

from .utils import PasswordChecker, request_is_ajax


class PasswordRotateMiddleware:
    """
    Adds Django message if password expires soon.
    Checks if user should be redirected to change password.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.password_status = "valid"
        if self.is_page_for_warning(request):
            force_password_change_path = reverse("force_password_change")
            # add warning if within the notification window for password expiration
            if request.user.is_authenticated:
                checker = PasswordChecker(request.user)
                msg = f"<a href='{force_password_change_path}'>Please change your password.</a> "
                if checker.is_expired():
                    if request.path != force_password_change_path:
                        msg += "It has expired."
                        self.add_warning(request, mark_safe(msg))
                        request.password_status = "expired"
                else:
                    time_to_expire_string = checker.get_expire_time()
                    request.password_status = "valid"
                    if time_to_expire_string and request.path != force_password_change_path:
                        msg += f"It expires in {time_to_expire_string}."
                        self.add_warning(request, mark_safe(msg))

        # picks up flag for forcing password change
        if hasattr(request, "redirect_to_password_change"):
            return redirect("force_password_change")

        # At this point, if the password expired, the user should have been redirected to force_password
        # change and should have changed her password.
        # If the user didn't change her password, redirect her until it's done.
        # If the password is still valid, just return the response.
        if request.password_status == "valid":
            return self.get_response(request)
        elif request.password_status == "expired":
            return redirect("force_password_change")

    def is_page_for_warning(self, request):
        """
        Only warn on pages that are GET requests and not ajax. Also ignore logouts.
        """
        if request.method == "GET" and not request_is_ajax(request):
            match = resolve(request.path)
            if match and match.url_name == "logout":
                return False
            return True
        return False

    def add_warning(self, request, text):
        storage = messages.get_messages(request)
        for message in storage:
            # only add this message once
            if message.extra_tags is not None and "password_rotate" in message.extra_tags:
                return
        messages.warning(request, text, extra_tags="password_rotate")
