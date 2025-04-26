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
# Generate your own secret key
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-fallback-key-for-dev') # Modified

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True' # Modified

ALLOWED_HOSTS = ['*'] # Adjust for production

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Add our app
    'requests_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
        # Add the app's template directory
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

# Use SQLite for simple local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# Consider PostgreSQL for production/Openshift

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'MST' # Adjust as needed

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' # Needed for production collection

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- AWX Configuration ---
# **IMPORTANT**: Use environment variables for sensitive data in production!
# Create a .env file in the project root for these
AWX_URL = os.getenv('AWX_URL', 'YOUR_AWX_URL_HERE') # e.g., https://awx.example.com
AWX_TOKEN = os.getenv('AWX_TOKEN', 'YOUR_AWX_API_TOKEN_HERE')
# The *numeric ID* of the Job Template in AWX to launch
AWX_JOB_TEMPLATE_ID = os.getenv('AWX_JOB_TEMPLATE_ID', 'YOUR_JOB_TEMPLATE_ID_HERE')

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    # Keep default if you use media files (not used in this project yet)
    # "default": {
    #     "BACKEND": "django.core.files.storage.FileSystemStorage",
    # },
}

# --- EMAIL CONFIGURATION ---
# For local development, print emails to the console:
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For production (using SMTP), configure these via environment variables:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.getenv('EMAIL_HOST')
# EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587)) # Default to 587 for TLS
# EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
# DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@example.com')
# SERVER_EMAIL = DEFAULT_FROM_EMAIL # Emails sent TO admins (e.g., on errors)

# --- APPLICATION SPECIFIC SETTINGS ---
IT_EMAIL_DISTRO_LIST = os.getenv('IT_EMAIL_DISTRO_LIST', 'it-support@example.com') # Get from .env

# --- JAZZMIN SETTINGS (Add this section at the end) ---
JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "ASAP Admin",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "ASAP Server Provisioning",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "ASAP",

    # Logo to use for your site, must be present in static files, used for brand on top left
    # "site_logo": "images/logo.png", # Optional: Requires static file setup

    # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
    # "login_logo": None, # Optional

    # CSS classes that are applied to the logo above
    # "site_logo_classes": "img-circle", # Optional

    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    # "site_icon": None, # Optional

    # Welcome text on the login screen
    "welcome_sign": "Welcome to the Server Provisioning Admin Portal",

    # Copyright on the footer
    "copyright": "",

    # The model admin to search from the search bar, search bar omitted if excluded
    "search_model": "requests_app.ServerRequest", # Direct search for requests

    # List of model admins to show search results for defined apps in search bar
    "related_modal_active": False,

    ############
    # Top Menu #
    ############

    # Links to put along the top menu
    "topmenu_links": [
        # Url that gets reversed (Permissions can be added)
        {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},
        {"model": "auth.User"},
        {"app": "requests_app"},
        {"name": "ASAP User Portal", "url": "/", "new_window": True},
    ],

    #############
    # Side Menu #
    #############

    # Whether to display the side menu
    "show_sidebar": True,

    # Whether to aut expand the menu
    "navigation_expanded": True,

    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": [],

    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [],

    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": ["requests_app", "auth"],

    # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,5.0.10,5.0.11,5.0.12,5.0.13,5.0.2,5.0.3,5.0.4,5.0.5,5.0.6,5.0.7,5.0.8,5.0.9,5.1.0,5.1.1,5.2.0,5.3.0,5.3.1,5.4.0,5.4.1,5.4.2,5.13.0,5.12.0,5.11.2,5.11.1,5.10.0,5.9.0,5.8.2,5.8.1,5.7.2,5.7.1,5.7.0,5.6.3,5.5.0,5.4.2
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": False,

    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    # "custom_css": None,
    "custom_js": None,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": False, # Set to True to easily experiment with themes

    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    # "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
}

# Optional: Further UI tweaks
JAZZMIN_UI_TWEAKS = {
    # Many options here: https://django-jazzmin.readthedocs.io/ui_tweaks/
    "theme": "darkly", # Try "darkly", "litera", "pulse", "sandstone", "united" etc.
    "dark_mode_theme": "darkly",
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