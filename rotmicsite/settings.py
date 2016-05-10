# Django settings for rotmicsite project.
import os.path as osp
import os

# Build paths inside the project like this: os.path.join(PROJECT_ROOT, ...)
PROJECT_ROOT = osp.dirname(osp.dirname(__file__))

###############################
## Dev / Production / Debugging

# distinguish development from production server
import sys
RUNNING_DEV_SERVER = ('manage.py' in sys.argv[0])

TEMPLATE_DEBUG = RUNNING_DEV_SERVER

if not RUNNING_DEV_SERVER:
    DEBUG = bool(os.environ.get('DEBUG', False))
else:
    DEBUG = True

# activate storage of uploaded files on Amazon AWS
USE_S3_STORAGE = not RUNNING_DEV_SERVER

#USE_S3_STORAGE = True

###############################
## Database and related config

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# Database configuration by Heroku $DATABASE_URL
# Use persistent connections
# https://devcenter.heroku.com/articles/django-app-configuration#database-connection-persistence
## this will be overriden by $DATABASE_URL configuration; sqlite is fall-back
DATABASES = { 
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'db.sqlite3'),
    }}

import dj_database_url
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

#############################
## Static files (CSS, JavaScript, Images)
## https://docs.djangoproject.com/en/1.9/howto/static-files/
## https://devcenter.heroku.com/articles/django-app-configuration#static-assets-and-file-serving

# Absolute path to the directory static files should be collected to.
STATIC_ROOT = osp.join(PROJECT_ROOT, 'rotmicsite','staticfiles')
# URL prefix for static files.
STATIC_URL = '/static/'
# Additional locations of static files
## STATICFILES_DIRS = ()

# List of finder classes that know how to find static files in various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

############################
## SSL / Encryption

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'settings-k^(3w9m#hndetog(ap+f(m+^jn*vu&s4a9cv3%&a(fe)$aq=s'
try:
    ## prepare env variable:
    ## heroku config:add DJANGO_SECRET_KEY="your_secret_key"
    ## Note: () are not tolerated in the key even using quotation marks
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', SECRET_KEY)
except:
    pass

#################################
## Storage of User-uploaded files

# Absolute path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = osp.join(PROJECT_ROOT, 'dev_uploads')

if USE_S3_STORAGE:
    from aws_settings import *
    ## sets MEDIA_URL and DEFAULT_FILE_STORAGE
else:
    # URL that handles the media served from MEDIA_ROOT. Make sure to use a
    # trailing slash.
    # Examples: "http://example.com/media/", "http://media.example.com/"
    MEDIA_URL = '/media/'

#########################
## Various settings

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = os.environ.get('TIME_ZONE', 'US/Eastern')

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = os.environ.get('LANGUAGE_CODE','en-us')

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# site-wide default for displaying dates
DATE_FORMAT = os.environ.get('DATE_FORMAT', 'Y-m-d')

DATETIME_FORMAT = os.environ.get('DATETIME_FORMAT', 'Y-m-d H:i')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)


TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.core.context_processors.static",
                               "django.core.context_processors.tz",
                               "django.contrib.messages.context_processors.messages",
                               "django.core.context_processors.request",
                               )

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'rotmicsite.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'rotmicsite.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # default
)
ANONYMOUS_USER_ID = -1

AUTH_PROFILE_MODULE = "rotmic.UserProfile"

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    
    'django_comments',
    'ratedcomments',
    'south',
    'selectable',
    'reversion',
    'rotmic',
    'django.contrib.admin',  ## last for lowest priority in template loading
)

if USE_S3_STORAGE:
    INSTALLED_APPS += ('storages',)

    
COMMENTS_APP = 'ratedcomments'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
