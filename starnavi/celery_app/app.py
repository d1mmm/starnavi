import vertexai
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from starnavi.ENV import PROJECT_AI_ID, DATABASE_URL, CELERY_BROKER, CELERY_BACKEND
from starnavi.services import credentials

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

celery_app = Celery(
    "tasks",
    broker=CELERY_BROKER,
    backend=CELERY_BACKEND,
    include=['starnavi.celery_app.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True
)


if __name__ == "__main__":
    vertexai.init(project=PROJECT_AI_ID, location="us-central1", credentials=credentials)
    celery_app.worker_main(['worker', '--loglevel=info'])
