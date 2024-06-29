import logging

from sqlalchemy import create_engine, Column, Integer, DateTime, func, String, ForeignKey, Boolean
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy_utils import database_exists, create_database

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    posts = relationship("Post", back_populates="owner")
    comments = relationship("Comment", back_populates="author")
    blocked_contents = relationship("ContentBlocked", back_populates="author")


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_answered = Column(Boolean, default=False)
    owner = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    blocked_content = relationship("ContentBlocked", back_populates="post", uselist=False)


class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=False)
    post_id = Column(Integer, ForeignKey('posts.id'))
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")


class ContentBlocked(Base):
    __tablename__ = 'block_contents'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=True, default=None)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    title = Column(String)
    post = relationship("Post", back_populates="blocked_content")
    author = relationship("User", back_populates="blocked_contents")


engine = create_engine('postgresql://postgres:1111@localhost:5432/starnavi')
SessionLocal = sessionmaker(bind=engine)

try:
    if not database_exists(engine.url):
        create_database(engine.url)
        Base.metadata.create_all(engine)
except SQLAlchemyError as e:
    logging.error(e)
    raise


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
