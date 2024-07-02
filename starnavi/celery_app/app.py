from celery import Celery

celery_app = Celery(
    "tasks",
    broker='redis://celery_app:6379/0',
    backend='redis://celery_app:6379/0'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
