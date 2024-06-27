from datetime import datetime, timedelta
from typing import List

import jwt
from fastapi import FastAPI, HTTPException, requests

from utils import (email_check, encryption, ALGORITHM, JWT_SECRET, users, posts, comments, get_validated_user_id,
                   get_new_id)
from models import Post, PostCreate, CommentCreate, Comment, User, UserCreate, UserLogin

app = FastAPI()


@app.post("/create_users/")
async def create_user(user: UserCreate):
    if not email_check(user.email):
        raise HTTPException(status_code=401, detail=f"The email {user.email} is invalid")
    email = next((u for u in users if u.email == user.email), None)
    if email:
        raise HTTPException(status_code=409, detail=f"User already exists with {user.email}")
    user_id = get_new_id(users)
    hashed_password = encryption(user.password)
    new_user = User(id=user_id, name=user.name, email=user.email, password=hashed_password)
    users.append(new_user)
    return {"status_code": 200, "message": "success"}


@app.post("/login/")
async def login(user_login: UserLogin):
    hashed_password = encryption(user_login.password)
    user = next((u for u in users if u.email == user_login.email and u.password == hashed_password), None)
    if not user:
        raise HTTPException(status_code=401, detail=f"The credentials are invalid")

    payload = {
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

    return {"data": {"name": user.name, "token": token}, "status_code": 200, "message": f"{user.name} login successfully"}


@app.post("/posts/", response_model=Post)
async def create_post(post: PostCreate, request: requests.Request):
    user_id = get_validated_user_id(request.headers)
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    new_post_id = get_new_id(posts)
    new_post = Post(id=new_post_id, user_id=user_id, title=post.title, content=post.content,
                    created_at=datetime.now())
    posts.append(new_post)
    return new_post


@app.get("/posts/", response_model=List[Post])
async def get_posts():
    return posts


@app.post("/comments/", response_model=Comment)
async def create_comment(comment: CommentCreate, request: requests.Request):
    user_id = get_validated_user_id(request.headers)
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    post = next((p for p in posts if p.id == comment.post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    new_comment_id = get_new_id(comments)
    new_comment = Comment(id=new_comment_id, user_id=user_id, post_id=comment.post_id, content=comment.content,
                          created_at=datetime.now())
    comments.append(new_comment)
    post.comments.append(new_comment)
    return new_comment


@app.get("/comments/", response_model=List[Comment])
async def get_comments():
    return comments


@app.get("/users/", response_model=List[User])
async def get_users():
    return users
