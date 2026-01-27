from fastapi.testclient import TestClient
from app import main

client = TestClient(main.app)

def test_create_user():
    res = client.post("/users/", json={"email":"hello123@gmail.com", "password":"password123"})
    print(res.json())
    assert res.status_code == 201
