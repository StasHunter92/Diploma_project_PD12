"""
WSGI config for Diploma_project_PD12 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""
import os

from django.core.wsgi import get_wsgi_application

# ----------------------------------------------------------------------------------------------------------------------
# Create Django WSGI application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Diploma_project_PD12.settings')
application = get_wsgi_application()
