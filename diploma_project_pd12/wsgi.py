"""
WSGI config for diploma_project_pd12 project.
It exposes the WSGI callable as a module-level variable named ``application``.
"""
import os

from django.core.wsgi import get_wsgi_application

# ----------------------------------------------------------------------------------------------------------------------
# Create Django WSGI application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diploma_project_pd12.settings')
application = get_wsgi_application()
