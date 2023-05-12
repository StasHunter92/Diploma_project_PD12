import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")
django.setup()

# ----------------------------------------------------------------------------------------------------------------------
# Pytest settings
pytest_plugins = "tests.fixtures"
