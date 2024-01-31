import os
from django.contrib.admin import templates


DEBUG = False
LANGUAGES = (("en", "English"),)
LANGUAGE_CODE = "en"
USE_TZ = False
USE_I18N = True
SECRET_KEY = "fake-key"
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

PASSWORD_ROTATE_SECONDS = 10 * 60  # 10 minutes
PASSWORD_ROTATE_WARN_SECONDS = 5 * 60  # 5 minutes
PASSWORD_ROTATE_HISTORY_COUNT = 3
PASSWORD_ROTATE_MAX_SIMILARITY_RATIO = 50

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "password_rotate",
]

MIDDLEWARE = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "password_rotate.middleware.PasswordRotateMiddleware",
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "TEST_NAME": ":memory:",
        "USER": "",
        "PASSWORD": "",
        "PORT": "",
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
     "NAME": "password_rotate.validators.NotPreviousPasswordValidator",
    },
]

ROOT_URLCONF = "password_rotate.tests.urls"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [templates.__path__[0]],
        'APP_DIRS': False,
        "OPTIONS": {
            "debug": DEBUG,
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                )
            ],
            "context_processors": (
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ),
        }
    }
]
