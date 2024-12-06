# backend/celery_app.py
import os
from celery import Celery

import logging
logging.basicConfig(level=logging.DEBUG)

REDIS_URL = os.getenv('REDIS_URL')
print(f"REDIS_URL: {REDIS_URL}")

# Initialize Celery
celery_app = Celery(
    'ai_automation_tool',
    broker=REDIS_URL,
    backend=REDIS_URL,
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
)
