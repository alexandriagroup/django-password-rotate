# Django password rotation app
This app provides configurable rotation of passwords.

## Features
 * Configurable password duration and warning duration
 * Visual warning to user using Django messages
 * Prevents user from accessing any page in after expiration unless the password is changed
 * Forces the new password to be different from previously used passwords
 * Prevents similar passwords (ex: "password1", "password2", ...)

## Requirements
This Django app requires Python >= 3.8 and has been tested with Django 4.2, 5.1 and 5.2.

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
 5. Add the pattern in the urls of your project:
 ```python
 urlpatterns = [
     ...
     path("password_rotate/", include("password_rotate.urls")),
 ]
 ```
 6. Configure the app in your settings:
    ```python
    # rotate passwords after 90 days
    PASSWORD_ROTATE_SECONDS = 90 * 24 * 60 * 60
    # start warning 10 days before expiration
    PASSWORD_ROTATE_WARN_SECONDS = 10 * 24 * 60 * 60
    # keep at most the 3 previous (encrypted) passwords
    PASSWORD_ROTATE_HISTORY_COUNT = 3
    # when changing the password, allow only a new password with similarity ratio greater than 50
    PASSWORD_ROTATE_MAX_SIMILARITY_RATIO = 50
    ```
 7. Run `python manage.py migrate` to create the required database tables.

If you want to exclude superusers from the password expiration, set this flag:
```python
PASSWORD_ROTATE_EXCLUDE_SUPERUSERS = True
```

## Acknowledgements
This app is a direct modification of:
- [django-password-expire](https://github.com/cash/django-password-expire)
- [django-password-policies](https://github.com/tarak/django-password-policies)
