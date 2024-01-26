from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from password_rotate.models import PasswordChange, PasswordHistory
from password_rotate.utils import PasswordChecker


def create_user(date_joined):
    user = get_user_model()(
        username="bob",
        email="bob@example.org",
        is_active=True,
        date_joined=date_joined,
    )
    user.set_password("password")
    user.save()
    return user


class PasswordCheckerTests(TestCase):
    def test_rotate_with_time_to_go_using_password_change_model(self):
        user = create_user(timezone.now())
        checker = PasswordChecker(user)
        self.assertFalse(checker.is_expired())

    def test_rotate_with_time_to_go_using_date_joined(self):
        user = create_user(timezone.now())
        PasswordChange.objects.all().delete()
        checker = PasswordChecker(user)
        self.assertFalse(checker.is_expired())

    def test_rotate_with_no_time_to_go_using_password_change_model(self):
        user = create_user(timezone.now())
        record = PasswordChange.objects.get(user=user)
        record.last_changed = timezone.now() - timedelta(seconds=settings.PASSWORD_ROTATE_SECONDS + 1)
        record.save()
        checker = PasswordChecker(user)
        self.assertTrue(checker.is_expired())

    def test_rotate_with_no_time_to_go_using_date_joined(self):
        join_date = timezone.now() - timedelta(seconds=settings.PASSWORD_ROTATE_SECONDS + 1)
        user = create_user(join_date)
        PasswordChange.objects.all().delete()
        checker = PasswordChecker(user)
        self.assertTrue(checker.is_expired())

    def test_warn_with_time_to_go_using_password_change_model(self):
        user = create_user(timezone.now())
        checker = PasswordChecker(user)
        self.assertFalse(checker.is_warning())

    def test_warn_with_time_to_go_using_date_joined(self):
        user = create_user(timezone.now())
        PasswordChange.objects.all().delete()
        checker = PasswordChecker(user)
        self.assertFalse(checker.is_warning())

    def test_warn_with_no_time_to_go_using_password_change_model(self):
        user = create_user(timezone.now())
        record = PasswordChange.objects.get(user=user)
        record.last_changed = timezone.now() - timedelta(seconds=settings.PASSWORD_ROTATE_SECONDS - 1)
        record.save()
        checker = PasswordChecker(user)
        self.assertTrue(checker.is_warning())
        self.assertFalse(checker.is_expired())

    def test_warn_with_no_time_to_go_using_date_joined(self):
        join_date = timezone.now() - timedelta(seconds=settings.PASSWORD_ROTATE_SECONDS - 1)
        user = create_user(join_date)
        PasswordChange.objects.all().delete()
        checker = PasswordChecker(user)
        self.assertTrue(checker.is_warning())
        self.assertFalse(checker.is_expired())


class PasswordValidatorsTests(TestCase):
    def setUp(self):
        PasswordChange.objects.all().delete()
        PasswordHistory.objects.all().delete()

    def test_password_never_used(self):
        """
        Updating the password with a password never used should be allowed
        """
        # ARRANGE
        user = create_user(timezone.now())
        credentials = {"username": "bob", "password": "password"}
        self.client.login(**credentials)

        # ACT
        response = self.client.post(
            reverse("force_password_change"),
            {
                "old_password": "password",
                "new_password1": "password1",
                "new_password2": "password1",
            }
        )

        # ASSERT
        # There should be no error message
        self.assertNotContains(
            response, "You already used this password.", status_code=302
        )

        self.assertEqual(PasswordChange.objects.all().count(), 1)
        # There should be 2 rows: password and password1
        self.assertEqual(PasswordHistory.objects.filter(user=user).count(), 2)

    def test_password_already_used(self):
        """
        Updating the password with a password already used should not be allowed
        """
        # ARRANGE
        user = create_user(timezone.now())
        credentials = {"username": "bob", "password": "password"}
        self.client.login(**credentials)

        # ACT
        # 1st password change, we use a new password
        response = self.client.post(
            reverse("force_password_change"),
            {
                "old_password": "password",
                "new_password1": "password1",
                "new_password2": "password1",
            }
        )
        pwcs = PasswordChange.objects.all()

        # 2nd password change, we use the initial password
        response = self.client.post(
            reverse("force_password_change"),
            {
                "old_password": "password1",
                "new_password1": "password",
                "new_password2": "password",
            }
        )

        # ASSERT
        # The user should be warned with an error message
        self.assertContains(
            response, "You already used this password.", status_code=200
        )

        # The password changed only the first time
        self.assertEqual(PasswordChange.objects.all().count(), 1)
        self.assertEqual(PasswordChange.objects.all()[0], pwcs[0])

        # There should be only 2 rows although 3 passwords where typed.
        # The last one is refused because it doesn't validate the
        # `password_rotate.validators.NotPreviousPasswordValidator`
        self.assertEqual(PasswordHistory.objects.filter(user=user).count(), 2)
