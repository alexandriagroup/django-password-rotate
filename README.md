# Django password rotation app
This app provides configurable rotation of passwords.

## Features
 * Configurable password duration and warning duration
 * Visual warning to user using Django messages
 * Prevents user from accessing any page in after expiration unless the password is changed
 * Forces the new password to be different from previously used passwords

## Requirements
This Django app requires Python >= 3.6 and has been tested with Django 2.2, 3.1, 3.2 and 4.2.

## Installation
 1. `pip install django-password-rotate`.
 2. Add `password_rotate` to `INSTALLED_APPS`.
 3. Add `'password_rotate.middleware.PasswordRotateMiddleware'` to `MIDDLEWARE`.
    It should be listed after authentication and session middlewares.
 4. Add `password_rotate.validators.NotPreviousPasswordValidator` to `AUTH_PASSWORD_VALIDATORS`:
 ```python
 AUTH_PASSWORD_VALIDATORS = [
 ...
 {
     "NAME": "password_rotate.validators.NotPreviousPasswordValidator",
 },
 ]
 ```
 5. Configure the app in your settings:
    ```python
    # rotate passwords after 90 days
    PASSWORD_ROTATE_SECONDS = 90 * 24 * 60 * 60
    # start warning 10 days before expiration
    PASSWORD_ROTATE_WARN_SECONDS = 10 * 24 * 60 * 60
    # keep at most the 3 previous (encrypted) passwords
    PASSWORD_ROTATE_HISTORY_COUNT = 3
    ```
 6. Run `python manage.py migrate` to create the required database tables.

If you want to exclude superusers from the password expiration, set this flag:
```python
PASSWORD_ROTATE_EXCLUDE_SUPERUSERS = True
```

## Acknowledgements
This app is a direct modification of:
- [django-password-expire](https://github.com/cash/django-password-expire)
- [django-password-policies](https://github.com/tarak/django-password-policies)
