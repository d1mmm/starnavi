from starnavi.celery_app.app import app, Session
from starnavi.database.db import Comment
from starnavi.services import automatic_ai_answer
from starnavi.utils import insert_into_db


@app.task
def send_automatic_reply(content, title, post_id):
    session = Session()
    response = automatic_ai_answer(content, title)
    ai_comment = Comment(user_id=1, post_id=post_id, content=response.text)
    insert_into_db(ai_comment, session)
    session.close()
