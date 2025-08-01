from datetime import timedelta
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from password_rotate.models import PasswordChange, PasswordHistory
from password_rotate.utils import PasswordChecker


def do_nothing(*args, **kwargs):
    pass


def create_user(username="bob", password="password", date_joined=timezone.now()):
    user = get_user_model()(
        username=username,
        email=f"{username}@example.org",
        is_active=True,
        date_joined=date_joined,
    )
    user.set_password(password)
    user.save()
    return user


class BaseTestCase(TestCase):
    def setUp(self):
        PasswordChange.objects.all().delete()
        PasswordHistory.objects.all().delete()

    def force_password_change(self, old, new):
        return self.client.post(
            reverse("force_password_change"),
            {
                "old_password": old, "new_password1": new, "new_password2": new,
            }
        )


class PasswordCheckerTests(BaseTestCase):
    def test_rotate_with_time_to_go_using_password_change_model(self):
        user = create_user(date_joined=timezone.now())
        checker = PasswordChecker(user)
        self.assertFalse(checker.is_expired())

    def test_rotate_with_time_to_go_using_date_joined(self):
        user = create_user(date_joined=timezone.now())
        PasswordChange.objects.all().delete()
        checker = PasswordChecker(user)
        self.assertFalse(checker.is_expired())

    def test_rotate_with_no_time_to_go_using_password_change_model(self):
        user = create_user(date_joined=timezone.now())
        record = PasswordChange.objects.get(user=user)
        record.last_changed = timezone.now() - timedelta(seconds=settings.PASSWORD_ROTATE_SECONDS + 1)
        record.save()
        checker = PasswordChecker(user)
        self.assertTrue(checker.is_expired())

    def test_rotate_with_no_time_to_go_using_date_joined(self):
        join_date = timezone.now() - timedelta(seconds=settings.PASSWORD_ROTATE_SECONDS + 1)
        user = create_user(date_joined=join_date)
        PasswordChange.objects.all().delete()
        checker = PasswordChecker(user)
        self.assertTrue(checker.is_expired())

    def test_warn_with_time_to_go_using_password_change_model(self):
        user = create_user(date_joined=timezone.now())
        checker = PasswordChecker(user)
        self.assertFalse(checker.is_warning())

    def test_warn_with_time_to_go_using_date_joined(self):
        user = create_user(date_joined=timezone.now())
        PasswordChange.objects.all().delete()
        checker = PasswordChecker(user)
        self.assertFalse(checker.is_warning())

    def test_warn_with_no_time_to_go_using_password_change_model(self):
        user = create_user(date_joined=timezone.now())
        record = PasswordChange.objects.get(user=user)
        record.last_changed = timezone.now() - timedelta(seconds=settings.PASSWORD_ROTATE_SECONDS - 1)
        record.save()
        checker = PasswordChecker(user)
        self.assertTrue(checker.is_warning())
        self.assertFalse(checker.is_expired())

    def test_warn_with_no_time_to_go_using_date_joined(self):
        join_date = timezone.now() - timedelta(seconds=settings.PASSWORD_ROTATE_SECONDS - 1)
        user = create_user(date_joined=join_date)
        PasswordChange.objects.all().delete()
        checker = PasswordChecker(user)
        self.assertTrue(checker.is_warning())
        self.assertFalse(checker.is_expired())


class PasswordValidatorsTests(BaseTestCase):
    def test_password_never_used(self):
        """
        Updating the password with a password never used should be allowed
        """
        # ARRANGE
        credentials = {"username": "bob", "password": "password"}
        user = create_user(**credentials)
        self.client.login(**credentials)

        # ACT
        response = self.force_password_change("password", "some new words")

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
        credentials = {"username": "bob", "password": "password"}
        user = create_user(**credentials)
        self.client.login(**credentials)

        # ACT
        # 1st password change, we use a new password
        response = self.force_password_change("password", "some new words")
        pwcs = PasswordChange.objects.all()
        # 2nd password change, we use the initial password
        response = self.force_password_change("some new words", "password")

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


class PasswordHistoryCountTest(BaseTestCase):
    def test_history_count(self):
        """
        The passwords stored in `PasswordHistory` should be limited
        to the latest `PASSWORD_ROTATE_HISTORY_COUNT`
        """
        # ARRANGE
        credentials = {"username": "bob", "password": "password"}
        create_user(**credentials)
        self.client.login(**credentials)

        raw_passwords = [
            "password",
            "Hello world",
            "Bonjour le monde",
            "Goodbye world",
            "Au revoir django",
        ]

        # ACT
        # We change the password PASSWORD_ROTATE_HISTORY_COUNT + 1 times
        for i in range(settings.PASSWORD_ROTATE_HISTORY_COUNT + 1):
            response = self.force_password_change(raw_passwords[i], raw_passwords[i+1])

        # ASSERT
        self.assertNotContains(response, "You already used this password.", status_code=302)
        self.assertEqual(PasswordChange.objects.count(), 1)
        self.assertEqual(PasswordHistory.objects.count(), settings.PASSWORD_ROTATE_HISTORY_COUNT)

        # Only the N latest passwords should be stored (N = PASSWORD_ROTATE_HISTORY_COUNT)
        encrypted_passwords = (
            PasswordHistory.objects.values_list("password", flat=True)
            .order_by("created")
        )
        # The first 2 passwords should be removed from PasswordHistory
        for raw, encrypted in zip(raw_passwords[2:], encrypted_passwords):
            hasher = identify_hasher(encrypted)
            # NOTE A password is verified if encrypt(raw) == encrypted
            self.assertTrue(hasher.verify(raw, encrypted))


class ForcePasswordChangeTests(BaseTestCase):
    @mock.patch("password_rotate.signals.messages", side_effect=do_nothing())
    def test_redirection_while_password_not_changed(self, messages):
        """
        When the password expired, while the user didn't change it, she should
        be redirected to the "force_password_change" url pattern.
        """
        # ARRANGE
        # The password expired
        user = create_user(date_joined=timezone.now())
        record = PasswordChange.objects.get(user=user)
        record.last_changed = timezone.now() - timedelta(seconds=settings.PASSWORD_ROTATE_SECONDS + 1)
        record.save()

        fpc_url = reverse("force_password_change")

        credentials = {"username": "bob", "password": "password"}
        self.client.login(**credentials)

        # ACT
        responses = {}
        responses["/some_page/"] = self.client.get("/some_page/")
        responses["/admin/"] = self.client.get("/admin/")
        responses[fpc_url] = self.client.get(fpc_url)

        # ASSERT
        self.assertEqual(responses["/some_page/"].status_code, 302)
        self.assertEqual(responses["/some_page/"]["Location"], fpc_url)
        self.assertEqual(responses["/admin/"].status_code, 302)
        self.assertEqual(responses["/admin/"]["Location"], fpc_url)
        self.assertEqual(responses[fpc_url].status_code, 200)

    @mock.patch("password_rotate.signals.messages", side_effect=do_nothing())
    def test_redirection_stops_after_password_change(self, messages):
        """
        When the password expired, while the user didn't change it, she should
        be redirected to the "force_password_change" url pattern.
        """
        # ARRANGE
        # The password expired
        user = create_user(date_joined=timezone.now())
        record = PasswordChange.objects.get(user=user)
        record.last_changed = timezone.now() - timedelta(seconds=settings.PASSWORD_ROTATE_SECONDS + 1)
        record.save()
        credentials = {"username": "bob", "password": "password"}
        self.client.login(**credentials)

        # ACT
        self.force_password_change("password", "some new words")

        # ASSERT
        self.assertEqual(self.client.get("/some_page/").status_code, 200)


class PasswordSimilarityRatioTest(BaseTestCase):
    def test_password_with_high_similarity(self):
        """
        When the new password is too similar to the old one, it should not be validated.
        """
        # ARRANGE
        user = create_user(date_joined=timezone.now())
        credentials = {"username": "bob", "password": "password"}
        self.client.login(**credentials)
        pwcs = PasswordChange.objects.all()

        # ACT
        # fuzz.ratio("password", "password1") gives a similarity of 94%
        # which is higher than the max similarity we set (30 %)
        response = self.force_password_change("password", "password1")

        # ASSERT
        # An error message. We should stay on this page.
        self.assertContains(
            response, "The new password is too similar to the old one.", status_code=200
        )

        # The password didn't change
        self.assertEqual(PasswordChange.objects.all().count(), 1)
        self.assertEqual(PasswordChange.objects.all()[0], pwcs[0])

        # There should be only 1 row
        self.assertEqual(PasswordHistory.objects.filter(user=user).count(), 1)

    def test_password_with_low_similarity(self):
        """
        When the similarity of the new password is low, it should be validated.
        """
        # ARRANGE
        user = create_user(date_joined=timezone.now())
        pwc = PasswordChange.objects.all()[0]
        credentials = {"username": "bob", "password": "password"}
        self.client.login(**credentials)

        # ACT
        # fuzz.ratio("password", "some new words")
        # gives a similarity of 45% which is lower than the max similarity we set (50 %)
        response = self.force_password_change("password", "some new words")

        # ASSERT
        # No error message and we should be redirected to password_change_done
        self.assertNotContains(
            response, "The new password is too similar to the old one.", status_code=302
        )
        self.assertEqual(response["Location"], reverse("password_change_done"))

        # The password changed
        self.assertEqual(PasswordChange.objects.all().count(), 1)
        self.assertGreater(PasswordChange.objects.all()[0].last_changed, pwc.last_changed)

        # There should be 2 rows
        self.assertEqual(PasswordHistory.objects.filter(user=user).count(), 2)
