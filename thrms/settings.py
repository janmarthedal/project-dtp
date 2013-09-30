import os
from django.contrib.messages import constants as message_constants

############ Site specific settings ############

if os.uname()[1].endswith('webfaction.com'):

    DEBUG = False

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'jmr_thrms_django',
            'USER': 'jmr_thrms_django',
            'PASSWORD': 'Cas250Tor_sql',
            'HOST': '',
            'PORT': '',
        }
    }

    STATIC_ROOT = '/home/jmr/webapps/thrms_static/'
    MEDIA_ROOT = '/home/jmr/webapps/thrms_media/'
    PROJECT_BASE = '/home/jmr/webapps/thrms_django/teoremer/'

    EMAIL_HOST = 'smtp.webfaction.com'
    EMAIL_HOST_USER = 'jmr'
    EMAIL_HOST_PASSWORD = 'Knuth316'
    DEFAULT_FROM_EMAIL = 'jmr@teoremer.com'
    SERVER_EMAIL = 'jmr@teoremer.com'
    ALLOWED_HOSTS = ['hilbert.janmr.com', 'teoremer.com']

    MESSAGE_LEVEL = message_constants.INFO

    SITE_URL = 'http://hilbert.janmr.com'  # used by browser_id

else:

    DEBUG = True
    INTERNAL_IPS = ('127.0.0.1', )  # to enable the debug variable in templates

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'thrms',
            'USER': 'root',
            'PASSWORD': 'Cas250Tor_sql',
            'HOST': '',
            'PORT': '',
        }
    }

    #STATIC_ROOT = '/home/jmr/www/static/'
    #MEDIA_ROOT = '/home/jmr/www/media/'
    PROJECT_BASE = '/home/jmr/projects/teoremer/'

    MESSAGE_LEVEL = message_constants.DEBUG

    SITE_URL = 'http://localhost:8000'  # used by browser_id

############ Common settings ############

ALLOWED_INCLUDE_ROOTS = ( PROJECT_BASE, )

ADMINS = (
#    ('Jan Marthedal Rasmussen', 'jmr@kanooth.com'),
    ('Jan Marthedal Rasmussen', 'jan.marthedal@gmail.com'),
)

MANAGERS = ADMINS

TEMPLATE_DEBUG = DEBUG

TEMPLATE_DIRS = (
    PROJECT_BASE + 'templates',
)

STATIC_URL = '/static/'
MEDIA_URL = '/media/files/'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Copenhagen'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'
#LANGUAGES = (
#    ('da', 'Danish'),
#    ('en', 'English'),
#)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'iw55d!*)!nw06xb1f-u@0c-nqga$6q1wm27_k^zo*a5^klyrq@'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
#    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django_browserid.context_processors.browserid'
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_browserid.auth.BrowserIDBackend',
)

MESSAGE_TAGS = {
    message_constants.DEBUG:   'label',
    message_constants.INFO:    'label label-info',
    message_constants.SUCCESS: 'label label-success',
    message_constants.WARNING: 'label label-warning',
    message_constants.ERROR:   'label label-important'
}

ROOT_URLCONF = 'thrms.urls'

BROWSERID_CREATE_USER = False
# Path to redirect to on successful login.
LOGIN_REDIRECT_URL = '/users/current'
# Path to redirect to on unsuccessful login attempt.
LOGIN_REDIRECT_URL_FAILURE = '/users/login-fail'
# Path to redirect to on logout.
LOGOUT_REDIRECT_URL = '/'

AUTH_USER_MODEL = 'users.User'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'thrms.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django_browserid',                # load after auth
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
    'drafts',
    'items',
    'users',
    'sources',
    'tags',
    'analysis',
    'api',
    'document',
)

LOGGING = {
    'version': 1,
#    'disable_existing_loggers': True,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s [%(asctime)s] %(module)s: %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': PROJECT_BASE + 'log/debug.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        '': {
            'handlers': ['file', 'console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'django.db.backends': {
            'handlers': ['file'],
            'propagate': False,
            'level': 'INFO',
        },
    }
}
