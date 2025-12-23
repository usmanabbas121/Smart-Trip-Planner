import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eld_api.settings')

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    import traceback
    def application(environ, start_response):
        error_msg = f"Django WSGI Error: {str(e)}\n\n{traceback.format_exc()}"
        start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
        return [error_msg.encode('utf-8')]

