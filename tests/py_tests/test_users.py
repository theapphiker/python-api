from app.database import client, setup_database

def test_create_user(client):
    res = client.post("/users/", json={"email":"hello123@gmail.com", "password":"password123"})
    print(res.json())
    assert res.status_code == 201

def test_login_user(client):
    res = client.post("/login", data={"username": "hello123@gmail.com", "password": "password123"})
    print(res.json())
    assert res.status_code == 200