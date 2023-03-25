"""
ASGI config for Diploma_project_PD12 project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# ----------------------------------------------------------------------------------------------------------------------
# Set the DJANGO_SETTINGS_MODULE environment variable to the project's settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Diploma_project_PD12.settings')

# ----------------------------------------------------------------------------------------------------------------------
# Create an ASGI application object using the project's settings module
application = get_asgi_application()
