import pytest
from app.database import pool
from app import main
from fastapi.testclient import TestClient

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
    user_data = {"email": "bobby@example.com", "password": "password123"}
    res = client.post("/users", json=user_data)

    assert res.status_code == 201

    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user