import os
from typing import Optional

import bcrypt

JWT_SECRET = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2Mj"
              "M5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")
KEY = bcrypt.gensalt()
ALGORITHM = "HS256"

PROJECT_AI_ID = os.getenv("STARNAVI_AI_ID")
CREDENTIALS = os.getenv("CREDENTIALS_AI", default="/app/service_account_key.json")
DATABASE_URL = os.getenv("STARNAVI_DB_URL")
