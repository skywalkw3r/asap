# provisioning_portal/settings.py

import os
from pathlib import Path
from dotenv import load_dotenv # Add this line

# Load environment variables from .env file
load_dotenv() # Add this line

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-fallback-key-for-dev')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*'] # Adjust for production

# Application definition

INSTALLED_APPS = [
    'jazzmin', # Add Jazzmin before default admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles', # Needed for collectstatic
    # Add our app
    'requests_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Whitenoise middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'provisioning_portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'requests_app/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'provisioning_portal.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# Consider PostgreSQL for production/Openshift using dj-database-url

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = 'static/'
# Directory where collectstatic will gather files for deployment
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Whitenoise Staticfiles Storage
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    # Keep default if you use media files (not used in this project yet)
    # "default": {
    #     "BACKEND": "django.core.files.storage.FileSystemStorage",
    # },
}

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- AWX Configuration ---
AWX_URL = os.getenv('AWX_URL', 'YOUR_AWX_URL_HERE')
AWX_TOKEN = os.getenv('AWX_TOKEN', 'YOUR_AWX_API_TOKEN_HERE')
AWX_JOB_TEMPLATE_ID = os.getenv('AWX_JOB_TEMPLATE_ID', 'YOUR_JOB_TEMPLATE_ID_HERE')

# --- EMAIL CONFIGURATION ---
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # Print emails to console for dev
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # For production SMTP
# EMAIL_HOST = os.getenv('EMAIL_HOST')
# EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
# EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
# DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'asap-noreply@yourcompany.com')
# SERVER_EMAIL = DEFAULT_FROM_EMAIL
DEFAULT_FROM_EMAIL = 'asap-portal@localhost' # Fallback for console backend

# --- APPLICATION SPECIFIC SETTINGS ---
IT_EMAIL_DISTRO_LIST = os.getenv('IT_EMAIL_DISTRO_LIST', 'it-support@example.com')

# --- JAZZMIN SETTINGS ---
JAZZMIN_SETTINGS = {
    "site_title": "ASAP Admin",
    "site_header": "ASAP Portal",
    "site_brand": "ASAP",
    "welcome_sign": "Welcome to the ASAP Admin Portal",
    "copyright": "ASAP Portal",
    "search_model": "requests_app.ServerRequest",
    "related_modal_active": False,
    "topmenu_links": [
        {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},
        {"model": "auth.User"},
        {"app": "requests_app"},
        {"name": "ASAP User Portal", "url": "/", "new_window": True},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["requests_app", "auth"],
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    # "related_modal_active": False, # Duplicate - removing
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
}

# --- JAZZMIN_UI_TWEAKS ---
JAZZMIN_UI_TWEAKS = {
    "theme": "simplex", # Red theme
    "navbar": "navbar-dark navbar-primary",
    "sidebar": "sidebar-dark-primary",
    "navbar_small_text": False,
    "footer_small_text": False,
    "sidebar_small_text": False,
    "brand_small_text": False,
    "accent": "accent-primary",
    "no_navbar_border": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "actions_sticky_top": True
}
