import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eld_api.settings')

from django.core.wsgi import get_wsgi_application

django_app = None

def application(environ, start_response):
    global django_app
    if django_app is None:
        try:
            django_app = get_wsgi_application()
        except Exception as e:
            import traceback
            error_msg = f"Django WSGI Error: {str(e)}\n\n{traceback.format_exc()}"
            start_response('500 Internal Server Error', [
                ('Content-Type', 'text/plain; charset=utf-8'),
                ('Content-Length', str(len(error_msg.encode('utf-8'))))
            ])
            return [error_msg.encode('utf-8')]
    
    return django_app(environ, start_response)

