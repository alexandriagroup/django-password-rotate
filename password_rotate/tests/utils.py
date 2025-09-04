from django.contrib.auth.management.commands import createsuperuser


def mock_password_input():
    """
    Decorator to temporarily replace input/getpass to allow interactive
    createsuperuser.

    Adapted/simplified from https://github.com/django/django/blob/5.2/tests/auth_tests/test_management.py#L45-L95
    """

    def inner(test_func):
        def wrapper(*args):
            class mock_getpass:
                @staticmethod
                def getpass(prompt=b"Password: ", stream=None):
                    return "password"

            old_getpass = createsuperuser.getpass
            createsuperuser.getpass = mock_getpass
            try:
                test_func(*args)
            finally:
                createsuperuser.getpass = old_getpass

        return wrapper

    return inner


class MockTTY:
    """
    A fake stdin object that pretends to be a TTY to be used in conjunction
    with mock_inputs.

    Copied from https://github.com/django/django/blob/5.2/tests/auth_tests/test_management.py#L98-L105
    """

    def isatty(self):
        return True
