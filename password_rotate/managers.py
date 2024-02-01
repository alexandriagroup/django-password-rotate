from django.db import models
from django.contrib.auth.hashers import identify_hasher
from django.conf import settings


class PasswordHistoryManager(models.Manager):
    default_offset = settings.PASSWORD_ROTATE_HISTORY_COUNT

    def delete_expired(self, user, offset=None):
        """
        Deletes expired password history entries from the database(s).

        :arg user: A :class:`~django.contrib.auth.models.User` instance.
        :arg int offset: A number specifying how much entries are to be kept
              in the user's password history. Defaults
              to :py:attr:`~settings.PASSWORD_ROTATE_HISTORY_COUNT`.
        """
        if not offset:
            offset = self.default_offset
        qs = self.filter(user=user)
        if qs.count() > offset:
            entry = qs[offset:offset + 1].get()
            qs.filter(created__lte=entry.created).delete()

    def check_password(self, user, raw_password):
        """
        Compares a raw (UNENCRYPTED!!!) password to entries in the users's
        password history.

        :arg object user: A :class:`~django.contrib.auth.models.User` instance.
        :arg str raw_password: A unicode string representing a password.
        :returns: ``False`` if a password has been used before, ``True`` if not.
        :rtype: bool
        """
        result = True
        if user.check_password(raw_password):
            result = False
        else:
            entries = self.filter(user=user).all()[:self.default_offset]
            for entry in entries:
                hasher = identify_hasher(entry.password)
                if hasher.verify(raw_password, entry.password):
                    result = False
                    break
        return result
