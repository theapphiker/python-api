import pytest
from app.database import pool
from app import main
from fastapi.testclient import TestClient
from app.oauth2 import create_access_token

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Open the pool before tests
    pool.open()

    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""TRUNCATE TABLE dev.users, dev.posts, dev.votes CASCADE;""")
            conn.commit()
    yield pool
    # Close the pool after all tests
    pool.close()

@pytest.fixture(scope="session")
def client(setup_database):
    yield TestClient(main.app)

@pytest.fixture(scope="session")
def test_user(client):
    user_data = {"email": "bobby99@example.com", "password": "password123"}
    res = client.post("/users", json=user_data)

    assert res.status_code == 201

    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user

@pytest.fixture(scope="session")
def test_user_no_login(client):
    user_data = {"email": "bobby111@example.com", "password": "pw"}
    res = client.post("/users", json=user_data)

    assert res.status_code == 201

    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user

@pytest.fixture(scope="session")
def token(test_user):
    return create_access_token({"user_id": test_user['id']})

@pytest.fixture(scope="session")
def bad_token(test_user_no_login):
    return "invalid"

@pytest.fixture
def unauthorized_client(client, bad_token):
    # Create a fresh client or use a new TestClient to avoid session-scope issues
    unauthorized = TestClient(main.app)
    unauthorized.headers = {
        **unauthorized.headers,
        "Authorization": f"Bearer {bad_token}"
    }
    return unauthorized

@pytest.fixture(scope="session")
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client

@pytest.fixture(scope="session")
def test_posts(test_user, setup_database):
    posts_data = [{
        "title": "first title",
        "content": "first content",
        "owner_id": test_user['id']
    }, {
        "title": "2nd title",
        "content": "2nd content",
        "owner_id": test_user['id']
    },
        {
        "title": "3rd title",
        "content": "3rd content",
        "owner_id": test_user['id']
    }]
    with setup_database.connection() as conn:
        with conn.cursor() as cursor:
            for post in posts_data:
                cursor.execute(
                """INSERT INTO dev.posts (title, content, user_id) 
                    VALUES (%s, %s, %s);""",
                (post['title'], post['content'], post["owner_id"]))
            conn.commit()
    return True

@pytest.fixture(scope="session")
def test_max_post_id(test_posts, setup_database):
    with setup_database.connection() as conn:
        with conn.cursor() as cursor:
                cursor.execute(
                """SELECT MAX(id) FROM dev.posts;""")
                max_id = cursor.fetchone()
    return max_id


