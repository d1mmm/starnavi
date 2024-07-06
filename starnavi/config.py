import logging
import os

import bcrypt

JWT_SECRET = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2Mj"
              "M5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")
KEY = bcrypt.gensalt()
ALGORITHM = "HS256"

try:
    PROJECT_AI_ID = os.getenv("STARNAVI_AI_ID")
    CREDENTIALS = os.getenv("CREDENTIALS_AI", default="/app/service_account_key.json")
    DATABASE_URL = os.getenv("STARNAVI_DB_URL")
    CELERY_BROKER = os.getenv("CELERY_BROKER_URL")
    CELERY_BACKEND = os.getenv("CELERY_BACKEND_URL")
except ValueError as v:
    logging.error(f"Environment variable is not set, {v}")
