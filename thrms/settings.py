import os
from django.contrib.messages import constants as message_constants

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

############ Site specific settings ############

if os.uname()[1].endswith('webfaction.com'):

    DEBUG = False

    LOG_FILE = os.path.join(BASE_DIR, '..', 'logs', 'info.log')
    STATIC_ROOT = '/home/jmr/webapps/thrms_static/'
    STATIC_URL = '/static/'
    MEDIA_ROOT = '/home/jmr/webapps/thrms_media/'
    MEDIA_URL = '/media/files/'

    ALLOWED_HOSTS = ['.janmr.com', 'teoremer.com']

    MESSAGE_LEVEL = message_constants.INFO

    SITE_URL = 'http://teoremer.com'

else:

    DEBUG = True
    INTERNAL_IPS = ('127.0.0.1', )  # to enable the debug variable in templates

    LOG_FILE = os.path.join(BASE_DIR, 'log', 'debug.log')
    STATIC_ROOT = '/home/jmr/www/static/'
    STATIC_URL = 'http://localhost/jmr/static/'
    MEDIA_ROOT = '/home/jmr/www/media/'
    MEDIA_URL = 'http://localhost/jmr/media/'

    MESSAGE_LEVEL = message_constants.DEBUG

    SITE_URL = 'http://localhost:8000'

############ Common settings ############

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'teoremer',
        'USER': 'jmr',
        'PASSWORD': 'JBfk40AM',
    }
}

EMAIL_HOST = 'smtp.webfaction.com'
EMAIL_HOST_USER = 'jmr'
EMAIL_HOST_PASSWORD = 'Knuth316'
DEFAULT_FROM_EMAIL = 'admin@teoremer.com'
SERVER_EMAIL = 'admin@teoremer.com'

ADMINS = (
    ('Jan Marthedal Rasmussen', 'jan.marthedal@gmail.com'),
)

MANAGERS = ADMINS
TEMPLATE_DEBUG = DEBUG

TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'templates'), )

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
# requires django.contrib.staticfiles.finders.FileSystemFinder in STATICFILES_FINDERS
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
#STATICFILES_FINDERS = (
#    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#)

# pipeline
STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'
PIPELINE_CSS = {
    'maincss': {
        'source_filenames': (
            'css/teoremer.css',
            'css/typeahead.js-bootstrap3.css',
        ),
        'output_filename': 'teoremer.css',
    },
}
PIPELINE_JS = {
    'mainjs': {
        'source_filenames': (
            'js/*.js',
        ),
        'output_filename': 'teoremer.js',
    },
}
PIPELINE_DISABLE_WRAPPER = True
#PIPELINE_ENABLED = True

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
    'users.helpers.CustomSocialAuthExceptionMiddleware',
    'main.badrequest.HandleBadRequest',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
)

MESSAGE_TAGS = {
    message_constants.DEBUG:   'label',
    message_constants.INFO:    'label label-info',
    message_constants.SUCCESS: 'label label-success',
    message_constants.WARNING: 'label label-warning',
    message_constants.ERROR:   'label label-danger'
}

ROOT_URLCONF = 'thrms.urls'

# Users and authentication

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = (
    'social.backends.google.GoogleOpenId',
    'social.backends.twitter.TwitterOAuth',
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.linkedin.LinkedinOAuth',
    'social.backends.persona.PersonaAuth',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = '/user/login'
LOGIN_REDIRECT_URL = '/user/current'
LOGOUT_REDIRECT_URL = '/'

SOCIAL_AUTH_STRATEGY = 'social.strategies.django_strategy.DjangoStrategy'
SOCIAL_AUTH_STORAGE = 'social.apps.django_app.default.models.DjangoStorage'
SOCIAL_AUTH_USER_FIELDS = ['email', 'fullname']

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'users.helpers.check_new_user',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
)

SOCIAL_AUTH_TWITTER_KEY = 'H77AtaP64G1xuWvuAI61w'
SOCIAL_AUTH_TWITTER_SECRET = 'imu1e8pl0zyXMe6oX2vJqxzCS4hcLJeAQPlfmWd3U'

SOCIAL_AUTH_FACEBOOK_KEY = '273595339457815'
SOCIAL_AUTH_FACEBOOK_SECRET = '3035f23f115e5df50f20a18717432293'
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']

SOCIAL_AUTH_LINKEDIN_KEY = '77uqs77i51tzhx'
SOCIAL_AUTH_LINKEDIN_SECRET = 'Zbqp19aBlck2yPoi'
SOCIAL_AUTH_LINKEDIN_SCOPE = ['r_basicprofile', 'r_emailaddress']
SOCIAL_AUTH_LINKEDIN_FIELD_SELECTORS = ['email-address']

############################

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'thrms.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'social.apps.django_app.default',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pipeline',
    'main',
    'drafts',
    'items',
    'users',
    'sources',
    'tags',
    'analysis',
    'api',
    'document',
    'media',
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
            'filename': LOG_FILE,
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
