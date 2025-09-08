# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\ecomm\celery.py

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomm.settings')

# Create a Celery instance and configure it with Django settings.
app = Celery('ecomm')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
