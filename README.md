# Starnavi Post and Comment Management API

**This project is a simple API for managing posts and comments with AI moderation and automatic response functionality. The API is developed using FastAPI and Pydantic**

# Features

* User Registration: Allows users to register.
* User Login: Allows users to log in.
* Post Management: API endpoints for creating, reading, updating, and deleting posts.
* Comment Management: API endpoints for creating, reading, updating, and deleting comments.
* Moderation: Checks posts and comments for offensive language or insults at the time of creation and blocks such posts or comments.
* Analytics: Provides analytics on the number of comments added to posts over a specific period.
* Automatic Reply: Provides an automatic reply to comments if enabled by the user for their posts. The automatic reply should not happen immediately but after a configured delay. The reply should be relevant to the post and the comment being replied to.

# Technologies

* Python 3.8
* FastAPI
* Pydantic
* PostgreSQL
* SQLAlchemy
* Alembic
* Gemini AI
* Redis
* Celery
* Docker
* Docker Compose

# Obtaining Google Cloud Credentials

**To enable AI moderation and automatic responses, you need to obtain credentials from Google Cloud:**

* Go to the https://console.cloud.google.com/
* Select your project or create a new one.
* Go to the APIs & Services. Enabled APIs & services
* Enable Vertex AI API
* Navigate to the "IAM & Admin" section and then "Service Accounts".
* Click on "Create Service Account".
* Fill in the required details and click "Create".
* Assign the necessary roles to the service account and click "Continue".
* Download the JSON key file and save it to your project directory as gcloud_credentials.json.

# Setup

**Clone the Repository**
    
   git clone https://github.com/yourusername/starnavi.git
     
**Add environment variables**

    export CREDENTIALS_AI=path to gcloud_credentials.json.
    export STARNAVI_AI_ID=project id
    export POSTGRES_USER=user
    export POSTGRES_PASSWORD=password
    export STARNAVI_DB_URL=postgresql://user:password@db:5432/starnavi
    export CELERY_BROKER_URL=redis://redis:port/0
    export CELERY_BACKEND_URL="redis://redis:port/0"
   
**Build the package**

    python3 setup.py sdist bdist_wheel

**Build the docker**

    docker-compose --profile default build # Build server
    docker-compose --profile tests build # Build tests
   
# Run

**Run starnavi/docker-compose.yml**

    docker-compose --profile default up
    docker-compose --profile tests up

**Or run in detached mode**

    docker-compose --profile default up -d
    docker-compose --profile tests up -d
    
# Example commands

    curl -X POST "http://0.0.0.0:8000/create_users/" -H "Content-Type: application/json" -d '{"name": "Name", "email": "email@gmail.com", "password": "123"}'
    curl -X POST "http://0.0.0.0:8000/login/" -H "Content-Type: application/json" -d '{"email": "email@gmail.com", "password": "123"}'
    curl -X POST "http://0.0.0.0:8000/posts/" -H "Authorization: token_after_login" -H "Content-Type: application/json" -d '{"title": "My first post", "content": "How are you ?", "should_be_answered": "True", "time_for_ai_answer": "10"}'
    curl -X POST "http://0.0.0.0:8000/comments/" -H "Authorization: token_after_login" -H "Content-Type: application/json" -d '{"post_id": "1", "content": "My first comment"}'
    curl -X GET "http://0.0.0.0:8000/comments/" -H "Authorization: token_after_login"
    curl -X GET "http://0.0.0.0:8000/api/comments-daily-breakdown?date_from=2024-07-02&date_to=2024-07-03" -H "Authorization: token_after_login"
    curl -X POST "http://0.0.0.0:8000/edit_post/" -H "Authorization: token_after_login" -H "Content-Type: application/json" -d '{"id": "1", "content": "Edited content post"}'
    curl -X POST "http://0.0.0.0:8000/edit_comment/" -H "Authorization: token_after_login" -H "Content-Type: application/json" -d '{"post_id": "1", "comment_id": "1", "content": "Edited comment"}'
    curl -X GET "http://0.0.0.0:8000/users/" -H "Authorization: token_after_login"
    curl -X GET "http://0.0.0.0:8000/posts/" -H "Authorization: token_after_login"
    curl -X GET "http://0.0.0.0:8000/blocked/" -H "Authorization: token_after_login"
    curl -X POST "http://0.0.0.0:8000/remove_comment/" -H "Authorization: token_after_login" -H "Content-Type: application/json" -d '{"post_id": "1", "comment_id": "1"}'
    curl -X POST "http://0.0.0.0:8000/remove_post/" -H "Authorization: token_after_login" -H "Content-Type: application/json" -d '{"id": "1"}'


# Contributing

**Feel free to submit issues and pull requests to contribute to the project.**

# License

**This project is licensed under the MIT License.**
