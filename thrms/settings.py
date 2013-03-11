import os

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
    PROJECT_BASE = '/home/jmr/webapps/thrms_django/thrms/'

else:

    DEBUG = True
    
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

    STATIC_ROOT = '/home/jmr/www/static/'
    PROJECT_BASE = '/home/jmr/projects/thrms/'

############ Common settings ############

ADMINS = (
    ('Jan Marthedal Rasmussen', 'jmr@kanooth.com'),
)

MANAGERS = ADMINS

TEMPLATE_DEBUG = DEBUG

TEMPLATE_DIRS = (
    PROJECT_BASE + 'templates',
)

STATIC_URL = '/static/'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Copenhagen'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

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
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'thrms.urls'

LOGIN_URL = '/user/login'

AUTH_USER_MODEL = 'users.User'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'thrms.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
#    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
#    'django.contrib.admin',
#    'south',
    'main',
    'items',
    'users',
    'refs',
    'admin',
    'tags',
    'analysis',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s [%(asctime)s] %(module)s: %(message)s'
            },
        'simple': {
            'format': '%(levelname)s %(message)s'
            },
        },
    'handlers': {
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
