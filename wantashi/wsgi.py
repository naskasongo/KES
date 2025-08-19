"""
WSGI config for wantashi project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""
import os
import logging
from django.core.wsgi import get_wsgi_application

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wantashi.settings')

application = get_wsgi_application()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wantashi.settings')

application = get_wsgi_application()


