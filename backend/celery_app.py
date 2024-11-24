# backend/celery_app.py

from celery import Celery

celery_app = Celery(
    'ai_automation_tool',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
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
