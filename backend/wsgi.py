import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, os.path.join(BASE_DIR, 'eld_api'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eld_api.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

