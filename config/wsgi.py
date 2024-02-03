import os
import sys
from pathlib import Path

# Add the project directory to the sys.path
ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.append(str(ROOT_DIR))

# Add the django_build_tool directory to sys.path
DJANGO_BUILD_TOOL_DIR = ROOT_DIR / 'django_build_tool'
sys.path.append(str(DJANGO_BUILD_TOOL_DIR))

# Add the AutomaticDjangoAuthentication directory to sys.path
AUTOMATIC_AUTH_DIR = DJANGO_BUILD_TOOL_DIR / 'AutomaticDjangoAuthentication'
sys.path.append(str(AUTOMATIC_AUTH_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
