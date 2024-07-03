import logging
from collections import defaultdict
from datetime import datetime, timedelta, date
from typing import List

import jwt
import uvicorn
from fastapi import FastAPI, HTTPException, requests, Depends, Query
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from database.db import Post, User, ContentBlocked, Comment, get_session
from services import analyze_content
from starnavi.celery_app.tasks import send_automatic_reply
from utils import (email_check, encryption, ALGORITHM, JWT_SECRET, get_validated_user_id, validate_jwt_token,
                   insert_into_db, create_ai_user_in_db)
from models import (PostCreate, CommentCreate, UserCreate, UserLogin, PostRemove, CommentRemove, PostEdit, CommentEdit,
                    PostModel, ContentBlockedModel, CommentModel, UserModel, CommentAnalytics)

app = FastAPI()
logging.basicConfig(filename='starnavi.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@app.post("/create_users/")
async def create_user(user: UserCreate, session: Session = Depends(get_session)):
    if session.query(User).first() is None:
        create_ai_user_in_db(session)

    if not email_check(user.email):
        raise HTTPException(status_code=401, detail=f"The email {user.email} is invalid")

    email = session.query(User).filter(User.email == user.email).first()
    if email:
        raise HTTPException(status_code=409, detail=f"User already exists with {user.email}")

    hashed_password = encryption(user.password)
    new_user = User(name=user.name, email=user.email, password=hashed_password)
    insert_into_db(new_user, session)
    return {"status_code": 200, "message": "success"}


@app.post("/login/")
async def login(user_login: UserLogin, session: Session = Depends(get_session)):
    hashed_password = encryption(user_login.password)
    user = session.query(User).filter(User.email == user_login.email and User.password == hashed_password).first()
    if not user:
        raise HTTPException(status_code=401, detail=f"The credentials are invalid")

    payload = {
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

    return {"data": {"name": user.name, "token": token}, "status_code": 200,
            "message": f"{user.name} login successfully"}


@app.post("/posts/", response_model=PostModel)
async def create_post(post: PostCreate, request: requests.Request, session: Session = Depends(get_session)):
    user_id = await get_validated_user_id(request.headers, session)
    if not analyze_content(post.content, post.title):
        new_block_content = ContentBlocked(user_id=user_id, title=post.title, content=post.content)
        insert_into_db(new_block_content, session)
        raise HTTPException(status_code=403, detail="Post was blocked")

    new_post = Post(user_id=user_id, title=post.title, content=post.content, should_be_answered=post.should_be_answered,
                    time_for_ai_answer=post.time_for_ai_answer)
    insert_into_db(new_post, session)
    return new_post


@app.post("/edit_post/", response_model=PostModel)
async def edit_post(edit: PostEdit, request: requests.Request, session: Session = Depends(get_session)):
    data = await validate_jwt_token(request.headers)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid Authentication token!")

    post = session.query(Post).filter(Post.id == edit.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if not analyze_content(edit.content):
        new_block_content = ContentBlocked(user_id=post.user_id, content=edit.content)
        insert_into_db(new_block_content, session)
        raise HTTPException(status_code=403, detail="Post content was blocked")
    post.content = edit.content
    session.commit()
    return post


@app.post("/remove_post/")
async def remove_post(remove: PostRemove, request: requests.Request, session: Session = Depends(get_session)):
    data = await validate_jwt_token(request.headers)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid Authentication token!")

    post = session.query(Post).filter(Post.id == remove.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    session.delete(post)
    session.commit()
    return {"status_code": 200, "message": "Post was deleted"}


@app.post("/comments/", response_model=CommentModel)
async def create_comment(comment: CommentCreate, request: requests.Request, session: Session = Depends(get_session)):
    user_id = await get_validated_user_id(request.headers, session)

    if not analyze_content(comment.content):
        new_block_content = ContentBlocked(user_id=user_id, post_id=comment.post_id, content=comment.content)
        insert_into_db(new_block_content, session)
        raise HTTPException(status_code=403, detail="Comment was blocked")

    post = session.query(Post).filter(Post.id == comment.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    new_comment = Comment(user_id=user_id, post_id=comment.post_id, content=comment.content)
    insert_into_db(new_comment, session)

    if post.should_be_answered:
        send_automatic_reply.apply_async((post.content, post.title, comment.post_id), countdown=post.time_for_ai_answer)

    return new_comment


@app.post("/edit_comment/", response_model=CommentModel)
async def edit_comment(edit: CommentEdit, request: requests.Request, session: Session = Depends(get_session)):
    data = await validate_jwt_token(request.headers)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid Authentication token!")

    post = session.query(Post).filter(Post.id == edit.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = session.query(Comment).filter(Comment.id == edit.comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if not analyze_content(edit.content):
        new_block_content = ContentBlocked(user_id=post.user_id, post_id=post.id, content=edit.content)
        insert_into_db(new_block_content, session)
        raise HTTPException(status_code=403, detail="Comment was blocked")

    comment.content = edit.content
    session.commit()
    return comment


@app.post("/remove_comment/")
async def remove_comment(remove: CommentRemove, request: requests.Request, session: Session = Depends(get_session)):
    data = await validate_jwt_token(request.headers)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid Authentication token!")

    post = session.query(Post).filter(Post.id == remove.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = session.query(Comment).filter(Comment.id == remove.comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    session.delete(comment)
    session.commit()
    return {"status_code": 200, "message": "Comment was deleted"}


@app.get("/posts/", response_model=List[PostModel])
async def get_posts(request: requests.Request, session: Session = Depends(get_session)):
    data = await validate_jwt_token(request.headers)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid Authentication token!")
    return session.query(Post).all()


@app.get("/blocked/", response_model=List[ContentBlockedModel])
async def get_blocked(request: requests.Request, session: Session = Depends(get_session)):
    data = await validate_jwt_token(request.headers)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid Authentication token!")
    return session.query(ContentBlocked).all()


@app.get("/comments/", response_model=List[CommentModel])
async def get_comments(request: requests.Request, session: Session = Depends(get_session)):
    data = await validate_jwt_token(request.headers)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid Authentication token!")
    return session.query(Comment).all()


@app.get("/users/", response_model=List[UserModel])
async def get_users(request: requests.Request, session: Session = Depends(get_session)):
    data = await validate_jwt_token(request.headers)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid Authentication token!")
    return session.query(User).all()


@app.get("/api/comments-daily-breakdown", response_model=List[CommentAnalytics])
async def get_comments_daily_breakdown(
        request: requests.Request,
        date_from: date = Query(..., description="Start date in format YYYY-MM-DD"),
        date_to: date = Query(..., description="End date in format YYYY-MM-DD"),
        session: Session = Depends(get_session)
):
    data = await validate_jwt_token(request.headers)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid Authentication token!")

    created_comments = session.query(
        func.date(Comment.created_at).label('date'),
        func.count(Comment.id).label('count')
    ).filter(
        and_(Comment.created_at >= date_from, Comment.created_at <= date_to)
    ).group_by(func.date(Comment.created_at)).all()

    blocked_comments = session.query(
        func.date(ContentBlocked.created_at).label('date'),
        func.count(ContentBlocked.id).label('count')
    ).filter(
        and_(ContentBlocked.created_at >= date_from, ContentBlocked.created_at <= date_to,
             ContentBlocked.post_id.isnot(None))
    ).group_by(func.date(ContentBlocked.created_at)).all()

    analytics = defaultdict(lambda: {"created": 0, "blocked": 0})

    for comment in created_comments:
        analytics[comment.date]["created"] += comment.count

    for comment in blocked_comments:
        analytics[comment.date]["blocked"] += comment.count

    result = []
    for comment_date, counts in analytics.items():
        result.append(CommentAnalytics(
            date=comment_date.strftime('%Y-%m-%d'),
            created_comments=counts["created"],
            blocked_comments=counts["blocked"]
        ))

    return result


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")
