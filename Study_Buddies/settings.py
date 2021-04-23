import os
import json
from pathlib import Path

with open('/etc/config.json') as config_file:
    config = json.load(config_file)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']

SITE_ID = 1


# Application definition

INSTALLED_APPS = [
    "users.apps.UsersConfig",
    "post.apps.PostConfig",
    "crispy_forms",
    "django_filters",
    "storages",
    "allauth",
    'channels',
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [ 
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "Study_Buddies.urls"

TEMPLATES = [ {
        "BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [], "APP_DIRS": True, "OPTIONS": {
            "context_processors": [ "django.template.context_processors.debug", "django.template.context_processors.request", "django.contrib.auth.context_processors.auth", "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "Study_Buddies.wsgi.application"


# Database https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = { "default": {
        "ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [ {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    { "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

ADMINS = [("chironsus", "zeyu.weng@gmail.com")]


# Internationalization https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images) https://docs.djangoproject.com/en/3.1/howto/static-files/

# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = "/static/" 
CRISPY_TEMPLATE_PACK = "bootstrap4"

MEDIA_ROOT = os.path.join(BASE_DIR, "media") 
MEDIA_URL = "/media/"

AUTHENTICATION_BACKENDS = ( "django.contrib.auth.backends.ModelBackend", "allauth.account.auth_backends.AuthenticationBackend",)

SOCIALACCOUNT_PROVIDERS = { 
        "google": {
        "SCOPE": [
            "profile", "email",
        ], "AUTH_PARAMS": {
            "access_type": "online",
        },
    }
}

LOGIN_REDIRECT_URL = "post-home" 
LOGIN_URL = "login"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com" 
EMAIL_PORT = 587 
EMAIL_USE_TLS = True 
EMAIL_HOST_USER = config.get("EMAIL_USER") 
EMAIL_HOST_PASSWORD = config.get("EMAIL_PASS")

AWS_ACCESS_KEY_ID = config.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = config.get("AWS_STORAGE_BUCKET_NAME")
AWS_STORAGE_BUCKET_NAME_RESIZED = config.get("AWS_STORAGE_BUCKET_NAME_RESIZED")
AWS_S3_REGION_NAME = config.get("AWS_S3_REGION_NAME")

AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
ASGI_APPLICATION = 'Study_Buddies.asgi.application'
