"""
WSGI config for rotmicsite project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

Adapted according to Heroku python-getting-started app.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
https://devcenter.heroku.com/articles/django-app-configuration
"""
import os

# We defer to a DJANGO_SETTINGS_MODULE already in the environment. This breaks
# if running multiple sites in the same mod_wsgi process. To fix this, use
# mod_wsgi daemon mode with each site in its own daemon process, or use
# os.environ["DJANGO_SETTINGS_MODULE"] = "rotmicsite.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rotmicsite.settings")

# support user upload of files with non-ascii file names
# see: https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/modwsgi/#if-you-get-a-unicodeencodeerror
# NOTE: neither of these variants is doing the trick if LANG
#       is defined wrongly in /etc/apache2/envvars (which it usually is)
#       apparently, envvars is overriding LANG *after* it has been set by wsgi.py 
os.environ['LANG'] = "en_US.UTF-8"     ## hard override of systems default
os.environ['LC_ALL'] = "en_US.UTF-8"

from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

application = get_wsgi_application()
application = DjangoWhiteNoise(application)
