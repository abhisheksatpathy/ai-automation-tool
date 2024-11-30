# backend/celery_app.py
import openai
print(f"Celery Worker - OpenAI version: {openai.__version__}")

import os
from celery import Celery

REDIS_URL = os.getenv('REDIS_URL')

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
    # Remove task_routes to use the default queue
    # task_routes={
    #     'tasks.generate_text': {'queue': 'default'},
    #     'tasks.display_text': {'queue': 'default'},
    # }
)
