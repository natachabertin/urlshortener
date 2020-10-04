from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

def test_create_user():
    response = client.post("/users/")
    assert response.status_code == 200
    # assert response.json() == {"msg": "Hello World"}

def test_read_users():
    response = client.get("/users/")
    assert response.status_code == 200
    assert response.json() == []

def test_read_user():
    response = client.get("/users/1")
    assert response.status_code == 200
    # assert response.json() == {"msg": "Hello World"}

def test_create_url_for_user():
    response = client.post("/users/1/urls/")
    assert response.status_code == 200
    # assert response.json() == {"msg": "Hello World"}

def test_read_urls():
    response = client.get("/urls/")
    assert response.status_code == 200
    assert response.json() == []

def test_create_click_for_url():
    response = client.post("/urls/{url_id}/clicks/")
    assert response.status_code == 200
    # assert response.json() == {"msg": "Hello World"}

def test_read_clicks():
    response = client.get("/clicks/")
    assert response.status_code == 200
    # assert response.json() == {"msg": "Hello World"}
