# -*- coding: utf-8 -*-

# Django settings for pv project.

import os.path

PROJECT_DIR = os.path.dirname(__file__)

DEBUG = True

ADMINS = ()

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_DIR, 'dev_data.sqlite'),
    },
    'nop': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_DIR, 'dev_nop.sqlite'),
    }
}

DATABASE_ROUTERS = ['nop.dbrouter.NopRouter']

TIME_ZONE = 'Europe/Vienna'

LANGUAGE_CODE = 'de'

SITE_ID = 1

USE_I18N = True
USE_L10N = True

LOCALE_PATHS = (
    os.path.join(PROJECT_DIR, 'locale'),
)

MEDIA_ROOT = os.path.join(PROJECT_DIR, 'site_media')
MEDIA_URL = '/site_media/'

STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
STATIC_URL = '/static/'

SECRET_KEY = ''

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'pv.urls'

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        #'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT AUTHENTICATION_CLASSES': [
    ]
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'program',
    'nop',
    'profile',
    'tinymce',
    'versatileimagefield',
    'rest_framework',
    'frapp',
)

THUMBNAIL_SIZES = ['640x480', '200x200', '150x150']

#TINYMCE_JS_URL = '/static/js/tiny_mce/tiny_mce.js'
TINYMCE_DEFAULT_CONFIG = {
    #'plugins': 'contextmenu',
    'selector': 'textarea',
    'theme': 'advanced',
    'theme_advanced_toolbar_location': 'top',
    'theme_advanced_buttons1' : 'bold,italic,underline,separator,bullist,numlist,separator,link,unlink,separator,undo,redo,separator,formatselect',
    'theme_advanced_blockformats': 'p,h1,h2,h3,blockquote',
    'theme_advanced_font_sizes': '14px,16px',
    'cleanup_on_startup': True,
    'width': 620,
    'height': 400,
}

CACHE_BACKEND = 'locmem://'

MUSIKPROG_IDS = (
    1,    # unmodieriertes musikprogramm
)
SPECIAL_PROGRAM_IDS = ()

# URL to CBA - Cultural Broadcasting Archive
CBA_URL = 'https://cba.fro.at'

# Contact cba@fro.at to be whitelisted and get an API KEY
# Leave empty to disable requests to CBA
CBA_API_KEY = ''

# URL to CBA ajax handler (used for retrieving additional data or increasing stream counter)
CBA_AJAX_URL = CBA_URL + '/wp-admin/admin-ajax.php'

# URL to CBA's REST API with trailing slash
CBA_REST_API_URL = CBA_URL + '/wp-json/wp/v2/'


try:
    from .local_settings import *
except ImportError:
    pass