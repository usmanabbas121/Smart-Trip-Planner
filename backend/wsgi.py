import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

os.environ['VERCEL'] = '1'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eld_api.settings')

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()

def application(environ, start_response):
    return app(environ, start_response)

