# Django password rotation app
This app provides configurable rotation of passwords.

**NOT USABLE YET!**

## Features
 * Configurable password duration and warning duration
 * Visual warning to user using Django messages
 * Prevents user from logging in after expiration

## Requirements
This Django app requires Python >= 3.6 and has been tested with Django 2.2, 3.1, 3.2 and 4.2.

## Installation
 1. `pip install django-password-rotate`.
 2. Add `password_rotate` to `INSTALLED_APPS`.
 3. Add `'password_rotate.middleware.PasswordRotateMiddleware'` to `MIDDLEWARE`.
    It should be listed after authentication and session middlewares.
 4. Configure the app in your settings:
    ```python
    # contact information if password is expired
    PASSWORD_ROTATE_CONTACT = "John Doe <jdoe@example.com>"
    # rotate passwords after 90 days
    PASSWORD_ROTATE_SECONDS = 90 * 24 * 60 * 60
    # start warning 10 days before expiration
    PASSWORD_ROTATE_WARN_SECONDS = 10 * 24 * 60 * 60
    ```
 5. Run `python manage.py migrate` to create the required database tables.

If you want to exclude superusers from the password expiration, set this flag:
```python
PASSWORD_ROTATE_EXCLUDE_SUPERUSERS = True
```

## Acknowledgements
This app is a direct modification of [django-password-expire](https://github.com/cash/django-password-expire).
