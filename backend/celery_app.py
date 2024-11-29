# backend/celery_app.py
import os
from celery import Celery

REDIS_CONNECTION_STRING = os.getenv('REDIS_URL')
components = REDIS_CONNECTION_STRING.split(',')
host_port = components[0]  
password = components[1].split('=')[1]  

# Check if SSL is enabled
ssl_enabled = 'ssl=True' in REDIS_CONNECTION_STRING

# Construct the broker URL
if ssl_enabled:
    broker_url = f'rediss://:{password}@{host_port}/0'
else:
    broker_url = f'redis://:{password}@{host_port}/0'

# Initialize Celery
celery_app = Celery(
    'ai_automation_tool',
    broker=broker_url,
    backend=broker_url,
    include=['tasks']
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Remove task_routes to use the default queue
    # task_routes={
    #     'tasks.generate_text': {'queue': 'default'},
    #     'tasks.display_text': {'queue': 'default'},
    # }
)
