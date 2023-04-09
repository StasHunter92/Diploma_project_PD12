"""
ASGI config for diploma_project_pd12 project.
It exposes the ASGI callable as a module-level variable named ``application``.
"""
import os

from django.core.asgi import get_asgi_application

# ----------------------------------------------------------------------------------------------------------------------
# Set the DJANGO_SETTINGS_MODULE environment variable to the project's settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diploma_project_pd12.settings')

# ----------------------------------------------------------------------------------------------------------------------
# Create an ASGI application object using the project's settings module
application = get_asgi_application()
