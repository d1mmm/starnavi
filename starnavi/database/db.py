from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from starnavi.config import DATABASE_URL
from starnavi.mixin import HelperModelMixin


class BaseModel(HelperModelMixin):
    pass


Base = declarative_base(cls=BaseModel)


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
    should_be_answered = Column(Boolean, default=False)
    time_for_ai_answer = Column(Integer, default=0)
    owner = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    blocked_content = relationship("ContentBlocked", back_populates="post", uselist=False)


class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=False)
    post_id = Column(Integer, ForeignKey('posts.id'))
    content = Column(String, nullable=False)
    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")


class ContentBlocked(Base):
    __tablename__ = 'block_contents'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=True, default=None)
    content = Column(String, nullable=False)
    title = Column(String)
    post = relationship("Post", back_populates="blocked_content")
    author = relationship("User", back_populates="blocked_contents")


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
