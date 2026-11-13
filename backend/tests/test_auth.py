from app.core.security import hash_password, verify_password
from tests.conftest import PASSWORD, login_headers, register_user


def test_register_success_hides_password_hash(client):
    resp = register_user(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["email"] == "asha@example.com"
    assert body["data"]["role"] == "student"
    assert "password" not in resp.text.lower()


def test_register_duplicate_email_conflict(client):
    register_user(client)
    resp = register_user(client, email="ASHA@example.com")  # case-insensitive duplicate
    assert resp.status_code == 409
    assert resp.json()["success"] is False


def test_register_cannot_choose_role(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"name": "Sneaky", "email": "s@example.com", "password": PASSWORD, "role": "admin"},
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["role"] == "student"


def test_register_weak_password_rejected(client):
    for bad in ["short1", "onlyletters", "12345678"]:
        resp = register_user(client, email="w@example.com", password=bad)
        assert resp.status_code == 422, bad
        assert resp.json()["success"] is False


def test_login_success_returns_tokens(client):
    register_user(client)
    resp = client.post(
        "/api/v1/auth/login", json={"email": "asha@example.com", "password": PASSWORD}
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["token_type"] == "bearer"
    assert data["access_token"] and data["refresh_token"]


def test_login_wrong_password_and_unknown_email_same_error(client):
    register_user(client)
    wrong = client.post("/api/v1/auth/login", json={"email": "asha@example.com", "password": "Nope12345"})
    unknown = client.post("/api/v1/auth/login", json={"email": "who@example.com", "password": "Nope12345"})
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json()["message"] == unknown.json()["message"]


def test_me_requires_authentication(client):
    assert client.get("/api/v1/auth/me").status_code == 401
    assert client.get("/api/v1/auth/me", headers={"Authorization": "Bearer garbage"}).status_code == 401


def test_me_returns_current_user(client):
    headers = login_headers(client)
    resp = client.get("/api/v1/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["email"] == "asha@example.com"


def test_refresh_issues_new_tokens(client):
    register_user(client)
    login = client.post("/api/v1/auth/login", json={"email": "asha@example.com", "password": PASSWORD})
    refresh_token = login.json()["data"]["refresh_token"]
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    new_access = resp.json()["data"]["access_token"]
    assert client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {new_access}"}).status_code == 200


def test_token_types_are_not_interchangeable(client):
    register_user(client)
    tokens = client.post(
        "/api/v1/auth/login", json={"email": "asha@example.com", "password": PASSWORD}
    ).json()["data"]
    # refresh token must not work as an access token
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['refresh_token']}"})
    assert resp.status_code == 401
    # access token must not work as a refresh token
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["access_token"]})
    assert resp.status_code == 401


def test_password_hashing_roundtrip():
    hashed = hash_password("Passw0rd123")
    assert hashed != "Passw0rd123"
    assert verify_password("Passw0rd123", hashed)
    assert not verify_password("wrong", hashed)
