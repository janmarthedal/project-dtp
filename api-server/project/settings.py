import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = ')o_i#tn$mh$wr5tw_t+q)+!=179cmbfra89w3xnek(@74&u06i'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    #'django.contrib.staticfiles',
    'main',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
]

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = False
USE_TZ = False

#STATIC_URL = '/static/'
