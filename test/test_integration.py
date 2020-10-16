import pytest
from fastapi.testclient import TestClient
import requests
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
    Base.metadata.drop_all(bind=engine)  # fast and untidy db_teardown after each test


def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "URL shortener"}


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

@pytest.mark.skip(
    'OUTDATED'
    'This can be done manually anymore to avoid messing with real data.'
    'I keep this test here only to show the API evolution.'
)
def test_create_click_for_url(client):
    client.post("/users/", json={"email": "user@mai.l", "password": "pwd"})
    data_url = {
      "short_url": "df4ed6g4",
      "long_url": "google.com/some/dir.pdf",
      "created": "2020-10-04T01:36:34.492000",
      "expiration_time": 10,
      "last_access": "2020-10-04T02:36:34.492000",
      "is_active": True,
      "deleted": "2020-10-04T03:03:34.492000",
      "campaign": "string"
    }
    client.post("/users/1/urls/", json=data_url)
    data_click = {
        "visited": "2020-10-04T22:16:29.488000",
        "referer": "string",
        "user_agent": "string",
        "viewport": "string"
    }
    response = client.post("/urls/1/clicks/", json=data_click)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}

@pytest.mark.skip('Needs to mock the URL creation. WORKING in browser')
def test_read_clicks(client):
    client.post("/users/", json={"email": "user@mai.l", "password": "pwd"})
    data_url = {
      "short_url": "df4ed6g4",
      "long_url": "google.com/some/dir.pdf",
      "created": "2020-10-04T01:36:34.492000",
      "expiration_time": 10,
      "last_access": "2020-10-04T02:36:34.492000",
      "is_active": True,
      "deleted": "2020-10-04T03:03:34.492000",
      "campaign": "string"
    }
    client.post("/users/1/urls/", json=data_url)
    data_click = {
        "visited": "2020-10-04T22:16:29.488000",
        "referer": "string",
        "user_agent": "string",
        "viewport": "string"
    }
    client.post("/urls/1/clicks/", json=data_click)
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


@pytest.mark.skip('banned. WORKING in browser')
def test_click_short_url_redirects_to_long_url_site(client):
    client.post("/users/", json={"email": "user@mai.l", "password": "pwd"})
    data_url = {
        "short_url": "moz",
        "long_url": "http://www.mozilla.org",
        "created": "2020-10-08T22:12:30.302Z",
        "expiration_time": 30,
        "last_access": "2020-10-08T22:12:30.302Z",
        "is_active": True,
        "deleted": "2020-10-08T22:12:30.302Z",
        "campaign": "hotsale"
    }
    client.post("/users/1/urls/", json=data_url)
    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19"
    }
    response = requests.get("http://127.0.0.1:8000/moz", headers=headers)
    assert response.status_code == 200
    assert "mozilla" in response.text


@pytest.mark.skip('banned. WORKING in browser')
def test_click_short_url_loads_click_metadata(client):
    client.post("/users/", json={"email": "user@mai.l", "password": "pwd"})
    data_url = {
        "short_url": "exa",
        "long_url": "http://www.example.org",
        "created": "2020-10-08T22:12:30.302Z",
        "expiration_time": 30,
        "last_access": "2020-10-08T22:12:30.302Z",
        "is_active": True,
        "deleted": "2020-10-08T22:12:30.302Z",
        "campaign": "hotsale"
    }
    client.post("/users/1/urls/", json=data_url)
    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19"
    }
    requests.get("http://127.0.0.1:8000/exa", headers=headers)
    response = client.get("/clicks/")
    assert response.json() == "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    assert response.json()[0]["user_agent"] == "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    assert response.json()[0]["referer"] is not None
    assert response.json()[0]["viewport"] is not None


@pytest.mark.skip('WORKING in browser')
def test_delete_disables_url(client):
    pass


@pytest.mark.skip('WORKING in browser')
def test_404_if_redirect_to_disabled(client):
    pass


@pytest.mark.skip('WORKING in browser')
def test_disabled_url_DOES_show_in_click_stats(client):
    pass


@pytest.mark.skip('WORKING in browser')
def test_disabled_url_doesnt_show_in_url_lists(client):
    pass


@pytest.mark.skip('test in browser')
def test_hasing_url(client):
    pass


@pytest.mark.skip('test in browser')
def test_unhashing_url(client):
    pass


@pytest.mark.skip('test in browser')
def test_hashing_pwd(client):
    pass


@pytest.mark.skip('test in browser')
def test_unhashing_pwd(client):
    pass


@pytest.mark.skip('test in browser')
def test_validate_repetition_short_on_custom_creation(client):
    """check if done by the schema"""
    pass


@pytest.mark.skip('test in browser')
def test_can_create_two_diff_shorts_for_one_long(client):
    """check that schema works like this as designed"""
    pass
