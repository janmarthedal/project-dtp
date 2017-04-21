import os
from . import secrets

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = secrets.SECRET_KEY

DEBUG = True
ALLOWED_HOSTS = ['*']
INTERNAL_IPS = ['127.0.0.1']

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'dtp',
            'USER': 'root',
            'PASSWORD': 'orangebear',
            'HOST': 'db',
            'PORT': '3306'
        }
    }

LOCAL_APPS = [
    'mathitems',
    'drafts',
    'validations',
    'concepts',
    'equations',
    'media',
    'keywords',
    'userdata',
    'main',
]

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
    'pipeline',
] + LOCAL_APPS

PIPELINE = {
    'STYLESHEETS': {
        'main': {
            'source_filenames': (
                'main/normalize.css',
                'main/mathjax.css',
                'main/main.less'
            ),
            'output_filename': 'main.css',
        },
    },
    'JAVASCRIPT': {
        'main': {
            'source_filenames': (
                'main/analytics.js',
                'main/watcher.js',
            ),
            'output_filename': 'main.js',
            'extra_context': {
                'defer': True,
            },
        }
    },
    'JS_WRAPPER': '%s',
    'YUGLIFY_BINARY': os.path.join(BASE_DIR, 'node_modules', '.bin', 'yuglify'),
    'COMPILERS': (
        'pipeline.compilers.less.LessCompiler',
    ),
    'LESS_BINARY': os.path.join(BASE_DIR, 'node_modules', '.bin', 'lessc'),
}

# By defining SOCIAL_AUTH_PIPELINE, we avoid a conflict between django-pipeline
# and python-social-auth
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.twitter.TwitterOAuth',
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = secrets.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = secrets.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET

SOCIAL_AUTH_TWITTER_KEY = secrets.SOCIAL_AUTH_TWITTER_KEY
SOCIAL_AUTH_TWITTER_SECRET = secrets.SOCIAL_AUTH_TWITTER_SECRET

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'project.wsgi.application'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Copenhagen'
USE_I18N = False
USE_L10N = False
USE_TZ = True
DATETIME_FORMAT = 'N j, Y, H:i'

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media-files')
MEDIA_URL = '/media-files/'

LOGIN_REDIRECT_URL = '/user/current'
LOGIN_URL = '/user/login'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

for app_name in LOCAL_APPS:
    LOGGING['loggers'][app_name] = {
        'handlers': ['file', 'console'],
        'level': 'DEBUG'  # if DEBUG else 'WARN'
    }
