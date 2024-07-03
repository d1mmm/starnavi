from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class UserModel(BaseModel):
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


class CommentModel(BaseModel):
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


class PostModel(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    comments: List[CommentModel] = []
    created_at: datetime


class PostCreate(BaseModel):
    title: str
    content: str
    should_be_answered: Optional[bool] = False
    time_for_ai_answer: Optional[int] = 0


class PostEdit(BaseModel):
    id: int
    content: str


class PostRemove(BaseModel):
    id: int


class ContentBlockedModel(BaseModel):
    id: int
    user_id: int
    post_id: Optional[int]
    content: str
    created_at: datetime
    title: Optional[str]


class CommentAnalytics(BaseModel):
    date: str
    created_comments: int
    blocked_comments: int
