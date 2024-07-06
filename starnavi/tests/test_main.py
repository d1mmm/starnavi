from datetime import date
from unittest.mock import patch, MagicMock
import pytest

from starnavi.celery_app.tasks import send_automatic_reply

from starnavi.database.db import User, Comment, Post, ContentBlocked
from starnavi.tests.conftest import generate_token


@pytest.mark.api
@patch('starnavi.database.db.get_session', autospec=True)
def test_create_user_success(mock_get_session, mock_session, client):
    mock_session.query.return_value.filter.return_value.first.return_value = None
    mock_get_session.return_value = mock_session

    response = client.post("/create_users/", json={
        "name": "Test User",
        "email": "test@gmail.com",
        "password": "testpassword"
    })

    assert response.status_code == 200
    assert response.json() == {"status_code": 200, "message": "success"}


@pytest.mark.api
@patch('starnavi.database.db.get_session', autospec=True)
def test_create_user_invalid_email(mock_get_session, mock_session, client):
    mock_session.query(User).first.return_value = None
    mock_get_session.return_value = mock_session

    response = client.post("/create_users/", json={
        "name": "Test User",
        "email": "invalidemail",
        "password": "testpassword"
    })

    assert response.status_code == 401
    assert response.json() == {"detail": "The email invalidemail is invalid"}


@pytest.mark.api
@patch('starnavi.database.db.get_session', autospec=True)
def test_create_user_already_exists(mock_get_session, mock_session, client):
    mock_session.query(User).filter().first.return_value = User(name="Test User", email="test@gmail.com",
                                                                password="testpassword")
    mock_get_session.return_value = mock_session

    response = client.post("/create_users/", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword"
    })

    assert response.status_code == 409
    assert response.json() == {"detail": "User already exists with test@example.com"}


@pytest.mark.api
@patch('starnavi.database.db.get_session', autospec=True)
def test_login_user(mock_get_session, mock_session, client):
    mock_session.query(User).filter().first.return_value = User(name="testuser", email="testuser@example.com",
                                                                password="password")
    mock_get_session.return_value = mock_session

    response = client.post("/login/", json={"email": "testuser@example.com", "password": "password"})
    assert response.status_code == 200
    assert response.json()["message"] == "testuser login successfully"


@pytest.mark.api
@patch('starnavi.database.db.get_session', autospec=True)
def test_login_invalid_credentials(mock_get_session, mock_session, client):
    mock_session.query(User).filter.return_value.first.return_value = None
    mock_get_session.return_value = mock_session

    response = client.post("/login/", json={"email": "invaliduser@example.com", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json() == {"detail": "The credentials are invalid"}


@pytest.mark.api
@patch('starnavi.utils.get_validated_user_id', autospec=True)
@patch('starnavi.services.analyze_content', autospec=True)
@patch('starnavi.database.db.get_session', autospec=True)
def test_create_post(mock_get_session, mock_analyze_content, mock_get_validated_user_id, mock_session, client):
    mock_get_validated_user_id.return_value = 1
    mock_analyze_content.return_value = True

    mock_get_session.return_value = mock_session

    response = client.post("/posts/", json={
        "title": "Test Post",
        "content": "This is a test post content",
        "should_be_answered": False,
        "time_for_ai_answer": 10
    }, headers={"Authorization": generate_token()})

    assert response.status_code == 200
    assert response.json()["title"] == "Test Post"
    assert response.json()["content"] == "This is a test post content"
    assert response.json()["id"] == 1
    assert response.json()["created_at"] == "2024-07-05T12:34:56"


@pytest.mark.api
@patch('starnavi.services.analyze_content', autospec=True)
@patch('starnavi.database.db.get_session', autospec=True)
def test_edit_post_success(mock_get_session, mock_analyze_content, mock_session, client):
    mock_analyze_content.return_value = True
    mock_post = Post(id=1, user_id=1, content="Old content")
    mock_session.query(Post).filter.return_value.first.return_value = mock_post

    def mock_update(instance):
        instance.title = "Test Post"
        instance.created_at = "2024-07-05T12:34:56"

    mock_session.commit.side_effect = lambda: mock_update(mock_post)

    mock_get_session.return_value = mock_session

    response = client.post("/edit_post/", json={
        "id": 1,
        "content": "New content"
    }, headers={"Authorization": generate_token()})

    assert response.status_code == 200
    assert response.json()["content"] == "New content"


@pytest.mark.api
@patch('starnavi.database.db.get_session', autospec=True)
def test_remove_post_success(mock_get_session, mock_session, client):
    mock_session.query(Post).filter.return_value.first.return_value = Post(id=1)
    mock_get_session.return_value = mock_session

    response = client.post("/remove_post/", json={"id": 1}, headers={"Authorization": generate_token()})

    assert response.status_code == 200
    assert response.json()["message"] == "Post was deleted"


@pytest.mark.api
@patch('starnavi.utils.get_validated_user_id', autospec=True)
@patch('starnavi.services.analyze_content', autospec=True)
@patch('starnavi.database.db.get_session', autospec=True)
def test_create_comment_success(mock_get_session, mock_analyze_content, mock_get_validated_user_id, mock_session, client):
    mock_get_validated_user_id.return_value = 1
    mock_analyze_content.return_value = True

    mock_session.query(Post).filter.return_value.first.return_value = Post(id=1, should_be_answered=False)

    mock_get_session.return_value = mock_session

    response = client.post("/comments/", json={
        "post_id": 1,
        "content": "This is a test comment"
    }, headers={"Authorization": generate_token()})

    assert response.status_code == 200
    assert response.json()["content"] == "This is a test comment"


@pytest.mark.api
@patch('starnavi.services.analyze_content', autospec=True)
@patch('starnavi.database.db.get_session', autospec=True)
def test_edit_comment_success(mock_get_session, mock_analyze_content, mock_session, client):
    mock_session.query(Post).filter.return_value.first.return_value = Post(id=1, user_id=1, content="Old content")
    mock_comment = Comment(id=1, user_id=1, post_id=1, content="Old content")
    mock_session.query(Comment).filter.return_value.first.return_value = mock_comment

    def mock_update(instance):
        instance.created_at = "2024-07-05T12:34:56"

    mock_session.commit.side_effect = lambda: mock_update(mock_comment)

    mock_analyze_content.return_value = True

    mock_get_session.return_value = mock_session

    response = client.post("/edit_comment/", json={
        "comment_id": 1,
        "post_id": 1,
        "content": "Updated content"
    }, headers={"Authorization": generate_token()})

    assert response.status_code == 200
    assert response.json()["content"] == "Updated content"


@pytest.mark.api
@patch('starnavi.database.db.get_session', autospec=True)
def test_remove_comment_success(mock_get_session, mock_session, client):
    mock_session.query(Comment).filter.return_value.first.return_value = Comment(id=1)

    mock_session.query(Post).filter.return_value.first.return_value = Post(id=1)
    mock_session.query(Comment).filter.first.return_value = Comment(id=1)
    mock_get_session.return_value = mock_session

    response = client.post("/remove_comment/", json={
        "comment_id": 1,
        "post_id": 1
    }, headers={"Authorization": generate_token()})

    assert response.status_code == 200
    assert response.json()["message"] == "Comment was deleted"


@pytest.mark.api
@patch('starnavi.database.db.get_session', autospec=True)
def test_get_posts(mock_get_session, mock_session, client):
    mock_session.query.return_value.all.return_value = [
        Post(id=1, user_id=1, title="Test Post", content="Test Content", comments=[], created_at="2024-07-05T12:34:56"),
        Post(id=2, user_id=2, title="Another Post", content="Another Content", comments=[],
             created_at="2024-07-05T12:35:56")
    ]
    mock_get_session.return_value = mock_session

    response = client.get("/posts/", headers={"Authorization": generate_token()})
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "user_id": 1, "title": "Test Post", "content": "Test Content", "comments": [],
         "created_at": "2024-07-05T12:34:56"},
        {"id": 2, "user_id": 2, "title": "Another Post", "content": "Another Content", "comments": [],
         "created_at": "2024-07-05T12:35:56"}
    ]


@pytest.mark.api
@patch('starnavi.database.db.get_session', autospec=True)
def test_get_comments(mock_get_session, mock_session, client):
    mock_session.query.return_value.all.return_value = [
        Comment(id=1, user_id=1, post_id=1, content="Comment 1", created_at="2024-07-05T12:36:56"),
        Comment(id=2, user_id=2, post_id=2, content="Comment 2", created_at="2024-07-05T12:37:56")
    ]
    mock_get_session.return_value = mock_session

    response = client.get("/comments/", headers={"Authorization": generate_token()})

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "user_id": 1, "post_id": 1, "content": "Comment 1", "created_at": "2024-07-05T12:36:56"},
        {"id": 2, "user_id": 2, "post_id": 2, "content": "Comment 2", "created_at": "2024-07-05T12:37:56"}
    ]


@pytest.mark.api
@patch('starnavi.database.db.get_session', autospec=True)
def test_get_users(mock_get_session, mock_session, client):
    mock_session.query.return_value.all.return_value = [
        User(id=1, name="user1", email="user1@example.com", password="qwert123"),
        User(id=2, name="user2", email="user2@example.com", password="qwert456")
    ]
    mock_get_session.return_value = mock_session

    response = client.get("/users/", headers={"Authorization": generate_token()})

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "user1", "email": "user1@example.com", "password": "qwert123"},
        {"id": 2, "name": "user2", "email": "user2@example.com", "password": "qwert456"}
    ]


@pytest.mark.api
@patch('starnavi.database.db.get_session', autospec=True)
def test_get_blocked(mock_get_session,  mock_session, client):
    mock_session.query.return_value.all.return_value = [
        ContentBlocked(id=1, user_id=1, post_id=1, content="Blocked Content 1", created_at="2024-07-05T12:38:56",
                       title=None),
        ContentBlocked(id=2, user_id=2, post_id=2, content="Blocked Content 2", created_at="2024-07-05T12:39:56",
                       title="Title Blocked")
    ]
    mock_get_session.return_value = mock_session

    response = client.get("/blocked/", headers={"Authorization": generate_token()})

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "user_id": 1, "post_id": 1, "content": "Blocked Content 1", "created_at": "2024-07-05T12:38:56",
         "title": None},
        {"id": 2, "user_id": 2, "post_id": 2, "content": "Blocked Content 2", "created_at": "2024-07-05T12:39:56",
         "title": "Title Blocked"}
    ]


@pytest.mark.api
@patch('starnavi.database.db.get_session', autospec=True)
def test_get_comments_daily_breakdown(mock_get_session, mock_session, client):
    created_comments = [
        MagicMock(date=date(2024, 7, 1), count=2),
        MagicMock(date=date(2024, 7, 2), count=1)
    ]

    blocked_comments = [
        MagicMock(date=date(2024, 7, 1), count=1),
        MagicMock(date=date(2024, 7, 2), count=1)
    ]

    def mock_query(*args, **kwargs):
        class MockQuery:
            def filter(self, *args, **kwargs):
                return self

            def group_by(self, *args, **kwargs):
                return self

            # check this
            def all(self):
                return created_comments if 'comments.created_at' in str(args[0]) else blocked_comments

        return MockQuery()

    mock_session.query.side_effect = mock_query

    mock_get_session.return_value = mock_session

    headers = {"Authorization": generate_token()}

    response = client.get("/api/comments-daily-breakdown", headers=headers, params={
        "date_from": "2024-07-01",
        "date_to": "2024-07-03"
    })

    assert response.status_code == 200
    assert response.json() == [
        {"date": "2024-07-01", "created_comments": 2, "blocked_comments": 1},
        {"date": "2024-07-02", "created_comments": 1, "blocked_comments": 1}
    ]


@pytest.mark.api
@patch('starnavi.utils.get_validated_user_id', autospec=True)
@patch('starnavi.services.analyze_content', autospec=True)
@patch('starnavi.database.db.get_session', autospec=True)
def test_comment_bad_content(mock_get_session, mock_analyze_content, mock_get_validated_user_id, mock_session, client):
    mock_get_validated_user_id.return_value = 1
    mock_analyze_content.return_value = False

    mock_get_session.return_value = mock_session

    response = client.post("/edit_comment/", json={
        "post_id": 1,
        "comment_id": 1,
        "content": "This content should be blocked"
    }, headers={"Authorization": generate_token()})

    assert response.status_code == 403
    assert response.json() == {"detail": "Comment was blocked"}


@pytest.mark.api
@patch('starnavi.utils.get_validated_user_id', autospec=True)
@patch('starnavi.services.analyze_content', autospec=True)
@patch('starnavi.celery_app.tasks.send_automatic_reply.apply_async', autospec=True)
@patch('starnavi.database.db.get_session', autospec=True)
def test_create_comment_should_be_answered(mock_get_session, mock_apply_async, mock_analyze_content,
                                           mock_get_validated_user_id, mock_session, client):
    mock_get_validated_user_id.return_value = 1
    mock_analyze_content.return_value = True

    mock_session.query(Post).filter.return_value.first.return_value = Post(id=1, title="Test Title",
                                                                           content="This is a test post content",
                                                                           should_be_answered=True)

    mock_get_session.return_value = mock_session

    response = client.post("/comments/", json={
        "post_id": 1,
        "content": "This is a test comment"
    }, headers={"Authorization": generate_token()})

    assert response.status_code == 200

    send_automatic_reply.apply_async(('Example comment content', 'Example comment title', 123), countdown=5)

    mock_apply_async.assert_called_with(
        ('Example comment content', 'Example comment title', 123),
        countdown=5
    )
