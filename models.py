from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    email: str
    password: str


class Comment(BaseModel):
    id: int
    user_id: int
    post_id: int
    content: str
    created_at: datetime


class Post(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    comments: List[Comment] = []
    created_at: datetime


class PostCreate(BaseModel):
    title: str
    content: str


class CommentCreate(BaseModel):
    post_id: int
    content: str


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str
