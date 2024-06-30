import logging
import re
from datetime import datetime

import bcrypt
import jwt
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .database.db import User

JWT_SECRET = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2Mj"
              "M5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")
KEY = bcrypt.gensalt()
ALGORITHM = "HS256"


def encryption(password):
    return bcrypt.hashpw(password.encode(), KEY).decode()


def create_ai_user_in_db(session: Session):
    hashed = encryption("gemini123")
    ai_user = User(name="Gemini", email="gemini@gmail.com", password=hashed)
    insert_into_db(ai_user, session)


def email_check(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if not (re.fullmatch(regex, email)):
        return False
    return True


def insert_into_db(obj, session: Session):
    try:
        session.add(obj)
        session.commit()
    except SQLAlchemyError as e:
        logging.error(f"Error occurred while executing SQL commands: {e}")
        session.rollback()
        raise HTTPException(status_code=502, detail=f'Bad Gateway {e}')


async def validate_jwt_token(headers):
    token = None
    if "Authorization" in headers:
        token = headers["Authorization"].split(" ")[0]
        if not token:
            raise HTTPException(status_code=400, detail="Authentication Token is missing!")

    try:
        data = jwt.decode(token, JWT_SECRET, ALGORITHM)
        current_email = data["email"]
        if current_email is None:
            raise HTTPException(status_code=401, detail="Invalid Authentication token!")

        expiration_datetime = datetime.utcfromtimestamp(data["exp"])
        current_time = datetime.utcnow()
        if current_time > expiration_datetime:
            raise HTTPException(status_code=401, detail="Token has expired")

        return data
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token is invalid")


async def get_validated_user_id(headers, session: Session):
    decoded_payload = await validate_jwt_token(headers)
    if not decoded_payload:
        raise HTTPException(status_code=401, detail="Invalid Authentication token!")

    current_user = session.query(User).filter(User.email == decoded_payload["email"]).first()

    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    return current_user.id
