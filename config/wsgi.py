import os
from whitenoise import WhiteNoise
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_root_path = os.path.join(BASE_DIR, 'staticfiles')
application = WhiteNoise(application, root=static_root_path)

# application = WhiteNoise(application, root='/home/devops-itc/www/simple/staticfiles') # linux
