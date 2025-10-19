

# """
# Django settings for ecommerce project.
# """

# from pathlib import Path
# import os
# # import dj_database_url  # optional, in case you later switch to PostgreSQL

# # --------------------------------------------------------
# # Basic paths
# # --------------------------------------------------------
# BASE_DIR = Path(__file__).resolve().parent.parent
# TEMPLATES_DIRS = BASE_DIR / 'templates'
# STATIC_DIR = BASE_DIR / 'static'
# STATIC_ROOT = BASE_DIR / 'staticfiles'
# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'

# LOGIN_URL = '/login'

# # --------------------------------------------------------
# # Security
# # --------------------------------------------------------
# SECRET_KEY = "django-insecure-ytii)867^q+8d7^elw)vsv354^u$x67c=lxt3@q34^pq=2n&2("
# DEBUG = False  # turn off debug for production

# # 👇 PythonAnywhere URL - replace 'dhirghayu' with your actual username
# ALLOWED_HOSTS = [
#     'dhirghayu.pythonanywhere.com', 
#     'localhost', 
#     '127.0.0.1'
# ]

# # --------------------------------------------------------
# # Installed apps
# # --------------------------------------------------------
# INSTALLED_APPS = [
#     "django.contrib.admin",
#     "django.contrib.auth",
#     "django.contrib.contenttypes",
#     "django.contrib.sessions",
#     "django.contrib.messages",
#     "django.contrib.staticfiles",
#     "product",
#     "adminpage",
#     "crispy_forms",
#     "crispy_tailwind",
#     "user",
#     "django_filters",
# ]

# CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
# CRISPY_TEMPLATE_PACK = "tailwind"

# # --------------------------------------------------------
# # Middleware
# # --------------------------------------------------------
# MIDDLEWARE = [
#     "django.middleware.security.SecurityMiddleware",
#     "whitenoise.middleware.WhiteNoiseMiddleware",  # ✅ Add this for serving static files
#     "django.contrib.sessions.middleware.SessionMiddleware",
#     "django.middleware.common.CommonMiddleware",
#     "django.middleware.csrf.CsrfViewMiddleware",
#     "django.contrib.auth.middleware.AuthenticationMiddleware",
#     "django.contrib.messages.middleware.MessageMiddleware",
#     "django.middleware.clickjacking.XFrameOptionsMiddleware",
# ]

# ROOT_URLCONF = "ecommerce.urls"

# TEMPLATES = [
#     {
#         "BACKEND": "django.template.backends.django.DjangoTemplates",
#         "DIRS": [TEMPLATES_DIRS],
#         "APP_DIRS": True,
#         "OPTIONS": {
#             "context_processors": [
#                 "django.template.context_processors.request",
#                 "django.contrib.auth.context_processors.auth",
#                 "django.contrib.messages.context_processors.messages",
#             ],
#         },
#     },
# ]

# WSGI_APPLICATION = "ecommerce.wsgi.application"

# # --------------------------------------------------------
# # Database
# # --------------------------------------------------------
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

# # --------------------------------------------------------
# # Password validation
# # --------------------------------------------------------
# AUTH_PASSWORD_VALIDATORS = [
#     {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
#     {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
#     {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
#     {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
# ]

# # --------------------------------------------------------
# # Internationalization
# # --------------------------------------------------------
# LANGUAGE_CODE = "en-us"
# TIME_ZONE = "UTC"
# USE_I18N = True
# USE_TZ = True

# # --------------------------------------------------------
# # Static files
# # --------------------------------------------------------
# STATIC_URL = "/static/"
# STATICFILES_DIRS = [STATIC_DIR]
# STATIC_ROOT = BASE_DIR / "staticfiles"

# # Use WhiteNoise to serve static files efficiently
# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# # --------------------------------------------------------
# # Default primary key field type
# # --------------------------------------------------------
# DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# # --------------------------------------------------------
# # Email
# # --------------------------------------------------------
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'dc.aloneboe@gmail.com'
# EMAIL_HOST_PASSWORD = 'dhfs fyjd fdjc wsfu'
# DEFAULT_FROM_EMAIL = 'dc.aloneboe@gmail.com'
# ADMIN_EMAIL = 'dc.aloneboe@gmail.com'

# # --------------------------------------------------------
# # Logging
# # --------------------------------------------------------
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': '{levelname} {asctime} {module} {message}',
#             'style': '{',
#         },
#     },
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#             'formatter': 'verbose',
#         },
#         'file': {
#             'class': 'logging.FileHandler',
#             'filename': BASE_DIR / 'email_errors.log',
#             'formatter': 'verbose',
#         },
#     },
#     'loggers': {
#         '': {
#             'handlers': ['console', 'file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }







# ====================================================
# +++++++++++++++++++++++++++++++++++++++
# ===================================================












"""
Django settings for ecommerce project.

Generated by 'django-admin startproject' using Django 5.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path
LOGIN_URL = '/login'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIRS = BASE_DIR / 'templates'

STATIC_DIR = BASE_DIR / 'static'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # ← ADD THIS LINE

# ↓↓↓ ADD THESE LINES FOR MEDIA FILES ↓↓↓
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# ↑↑↑ ADD THESE LINES FOR MEDIA FILES ↑↑↑


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-ytii)867^q+8d7^elw)vsv354^u$x67c=lxt3@q34^pq=2n&2("

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'product',
    'adminpage',
    "crispy_forms",
    "crispy_tailwind",
    'user',
    'django_filters',
]


CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"

CRISPY_TEMPLATE_PACK = "tailwind"


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ecommerce.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATES_DIRS],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ecommerce.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


STATICFILES_DIRS = [STATIC_DIR]



# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'dc.aloneboe@gmail.com'  # Replace with your Gmail address
EMAIL_HOST_PASSWORD = 'dhfs fyjd fdjc wsfu'  # Generate from Gmail (see below)
DEFAULT_FROM_EMAIL = 'dc.aloneboe@gmail.com'
ADMIN_EMAIL = 'dc.aloneboe@gmail.com'  # Replace with your admin email




LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'email_errors.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}