from sqlalchemy.orm import Session

from starnavi.celery_app.app import celery_app
from starnavi.utils import insert_into_db


@celery_app.task
def send_automatic_reply(ai_comment, session: Session):
    insert_into_db(ai_comment, session)