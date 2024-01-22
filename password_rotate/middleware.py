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
        if self.is_page_for_warning(request):
            password_change_path = reverse("password_change")
            # add warning if within the notification window for password expiration
            if request.user.is_authenticated:
                checker = PasswordChecker(request.user)
                msg = f"<a href='{password_change_path}'>Please change your password.</a> "
                if checker.is_expired():
                    if request.path != password_change_path:
                        msg += "It has expired."
                        self.add_warning(request, mark_safe(msg))
                else:
                    time_to_expire_string = checker.get_expire_time()
                    if time_to_expire_string and request.path != password_change_path:
                        msg += f"It expires in {time_to_expire_string}."
                        self.add_warning(request, mark_safe(msg))

        response = self.get_response(request)

        # picks up flag for forcing password change
        if getattr(request, "redirect_to_password_change", False):
            return redirect("password_change")

        return response

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
