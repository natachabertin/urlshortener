import pytest
from fastapi.testclient import TestClient

from main import app, get_db
from database import Base
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker


@pytest.fixture
def client():
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)  # db_teardown


def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}


def test_create_user(client):
    response = client.post(
        "/users/",
        json={
          "email": "user@mai.l",
          "password": "pwd"
        }
    )
    assert response.status_code == 200
    assert response.json() == {'email': 'user@mai.l', 'id': 1, 'urls': []}


def test_read_users(client):
    client.post(
        "/users/",
        json={
          "email": "user@mai.l",
          "password": "pwd"
        }
    )
    response = client.get("/users/")
    assert response.status_code == 200
    assert response.json() == [{'email': 'user@mai.l', 'id': 1, 'urls': []}]


def test_read_user(client):
    client.post(
        "/users/",
        json={
          "email": "user@mai.l",
          "password": "pwd"
        }
    )
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json() == {'email': 'user@mai.l', 'id': 1, 'urls': []}


def test_create_url_for_user(client):
    client.post("/users/", json={"email": "user@mai.l", "password": "pwd"})
    data = {
      "short_url": "df4ed6g4",
      "long_url": "google.com/some/dir.pdf",
      "created": "2020-10-04T01:36:34.492000",
      "expiration_time": 10,
      "last_access": "2020-10-04T02:36:34.492000",
      "is_active": True,
      "deleted": "2020-10-04T03:03:34.492000",
      "campaign": "string"
    }
    response = client.post("/users/1/urls/", json=data)
    assert response.status_code == 200
    assert response.json() == {
        "clicks": [],
        "id": 1,
        "owner_id": 1,
        "short_url": "df4ed6g4",
        "long_url": "google.com/some/dir.pdf",
        "created": "2020-10-04T01:36:34.492000",
        "expiration_time": 10,
        "last_access": "2020-10-04T02:36:34.492000",
        "is_active": True,
        "deleted": "2020-10-04T03:03:34.492000",
        "campaign": "string"
    }


def test_read_urls(client):
    client.post("/users/", json={"email": "user@mai.l", "password": "pwd"})
    data = {
      "short_url": "df4ed6g4",
      "long_url": "google.com",
      "created": "2020-10-04T01:36:34.492000",
      "expiration_time": 10,
      "last_access": "2020-10-04T02:36:34.492000",
      "is_active": True,
      "deleted": "2020-10-04T03:03:34.492000",
      "campaign": "string"
    }
    client.post("/users/1/urls/", json=data)
    response = client.get("/urls/")
    assert response.status_code == 200
    assert response.json() == [{
        "clicks": [],
        "id": 1,
        "owner_id": 1,
        "short_url": "df4ed6g4",
        "long_url": "google.com",
        "created": "2020-10-04T01:36:34.492000",
        "expiration_time": 10,
        "last_access": "2020-10-04T02:36:34.492000",
        "is_active": True,
        "deleted": "2020-10-04T03:03:34.492000",
        "campaign": "string"
    }]


def test_create_click_for_url(client):
    client.post("/users/", json={"email": "user@mai.l", "password": "pwd"})
    dataUrl = {
      "short_url": "df4ed6g4",
      "long_url": "google.com/some/dir.pdf",
      "created": "2020-10-04T01:36:34.492000",
      "expiration_time": 10,
      "last_access": "2020-10-04T02:36:34.492000",
      "is_active": True,
      "deleted": "2020-10-04T03:03:34.492000",
      "campaign": "string"
    }
    client.post("/users/1/urls/", json=dataUrl)
    dataClick = {
        "visited": "2020-10-04T22:16:29.488000",
        "referer": "string",
        "user_agent": "string",
        "viewport": "string"
    }
    response = client.post("/urls/1/clicks/", json=dataClick)
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "link_id": 1,
        "visited": "2020-10-04T22:16:29.488000",
        "referer": "string",
        "user_agent": "string",
        "viewport": "string"
    }


def test_read_clicks(client):
    client.post("/users/", json={"email": "user@mai.l", "password": "pwd"})
    dataUrl = {
      "short_url": "df4ed6g4",
      "long_url": "google.com/some/dir.pdf",
      "created": "2020-10-04T01:36:34.492000",
      "expiration_time": 10,
      "last_access": "2020-10-04T02:36:34.492000",
      "is_active": True,
      "deleted": "2020-10-04T03:03:34.492000",
      "campaign": "string"
    }
    client.post("/users/1/urls/", json=dataUrl)
    dataClick = {
        "visited": "2020-10-04T22:16:29.488000",
        "referer": "string",
        "user_agent": "string",
        "viewport": "string"
    }
    client.post("/urls/1/clicks/", json=dataClick)
    response = client.get("/clicks/")
    assert response.status_code == 200
    assert response.json() == [{
        "id": 1,
        "link_id": 1,
        "visited": "2020-10-04T22:16:29.488000",
        "referer": "string",
        "user_agent": "string",
        "viewport": "string"
    }]
