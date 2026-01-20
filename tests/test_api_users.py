# tests/test_api_users.py
import backend.routers.users as users_router


def test_users_create_ok(client, monkeypatch):
    monkeypatch.setattr(users_router.db, "insertUser", lambda **kwargs: 1)

    payload = {
        "login": "bob",
        "email": "bob@example.com",
        "nom": "Bob",
        "prenom": "Bobby",
        "hpwd": "secret",
        "birthday": "2001-02-03",
        "promo_id": "Intranet",
        "teacher": False,
        "superuser": False,
        "noteKfet": "Hello",
    }
    r = client.post("/api/users/create", json=payload)
    assert r.status_code == 201
    assert r.json()["login"] == "bob"


def test_users_create_conflict(client, monkeypatch):
    monkeypatch.setattr(users_router.db, "insertUser", lambda **kwargs: -1)

    payload = {
        "login": "bob",
        "email": "bob@example.com",
        "nom": "Bob",
        "prenom": "Bobby",
        "hpwd": "secret",
        "birthday": "2001-02-03",
        "promo_id": "Intranet",
        "teacher": False,
        "superuser": False,
        "noteKfet": "Hello",
    }
    r = client.post("/api/users/create", json=payload)
    assert r.status_code == 409


def test_users_create_rejects_sql_chars(client):
    payload = {
        "login": "bob;DROP",
        "email": "bob@example.com",
        "nom": "Bob",
        "prenom": "Bobby",
        "hpwd": "secret",
        "birthday": "2001-02-03",
        "promo_id": "Intranet",
        "teacher": False,
        "superuser": False,
        "noteKfet": "Hello",
    }
    r = client.post("/api/users/create", json=payload)
    assert r.status_code == 406


def test_users_me_ok(client, monkeypatch):
    monkeypatch.setattr(users_router.db, "get_user", lambda login: {"login": login})
    r = client.get("/api/users/me")
    assert r.status_code == 200
    assert r.json()["login"] == "admin"


def test_users_all_superuser_ok(client, monkeypatch):
    monkeypatch.setattr(users_router.db, "check_superuser", lambda login: 1)
    monkeypatch.setattr(users_router.db, "user_getall", lambda: {"bob": {"email": "x"}})

    r = client.get("/api/users/all")
    assert r.status_code == 200
    assert "bob" in r.json()


def test_users_all_not_superuser(client, monkeypatch):
    monkeypatch.setattr(users_router.db, "check_superuser", lambda login: -1)
    r = client.get("/api/users/all")
    assert r.status_code == 401
