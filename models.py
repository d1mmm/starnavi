from datetime import datetime
from typing import List

from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    email: str
    password: str


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class Comment(BaseModel):
    id: int
    user_id: int
    post_id: int
    content: str
    created_at: datetime


class CommentCreate(BaseModel):
    post_id: int
    content: str


class CommentEdit(BaseModel):
    post_id: int
    comment_id: int
    content: str


class CommentRemove(BaseModel):
    post_id: int
    comment_id: int


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


class PostEdit(BaseModel):
    id: int
    content: str


class PostRemove(BaseModel):
    id: int
