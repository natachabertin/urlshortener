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
    Base.metadata.drop_all(bind=engine) # db_teardown


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
    response = client.post("/users/1/urls/")
    assert response.status_code == 422
    assert response.json() == False

def test_read_urls(client):
    response = client.get("/urls/")
    assert response.status_code == 200
    assert response.json() == []

def test_create_click_for_url(client):
    response = client.post("/urls/{url_id}/clicks/")
    assert response.status_code == 200
    # assert response.json() == {"msg": "Hello World"}

def test_read_clicks(client):
    response = client.get("/clicks/")
    assert response.status_code == 200
    # assert response.json() == {"msg": "Hello World"}
