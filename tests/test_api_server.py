# tests/test_api_server.py
import os
import backend.server as server


def test_root(client):
    r = client.get("/api/")
    assert r.status_code == 200
    assert r.json()["message"].lower().startswith("welcome")


def test_version(client):
    r = client.get("/api/version")
    assert r.status_code == 200
    assert "version" in r.json()


def test_classrooms_all(client):
    r = client.get("/api/classrooms/all")
    assert r.status_code == 200
    assert "2Z34" in r.json()


def test_classrooms_all_detail(client):
    r = client.get("/api/classrooms/all/detail")
    assert r.status_code == 200
    data = r.json()
    assert "1" in data  # classroom_id=1 as string key (JSON)
    assert data["1"]["location"] == "2Z34"


def test_calendars_available(client, monkeypatch):
    monkeypatch.setattr(server, "load_inverse_promos", lambda: ["Intranet", "M1_E3A"])
    r = client.get("/api/calendars/available")
    assert r.status_code == 200
    assert r.json() == ["Intranet", "M1_E3A"]


def test_csv_invalid_name(client):
    r = client.get("/api/csv", params={"promo_str": "BAD NAME!"})
    assert r.status_code == 406


def test_csv_promo_not_found(client):
    r = client.get("/api/csv", params={"promo_str": "NO_SUCH_PROMO"})
    assert r.status_code == 418


def test_csv_ok_creates_file(client, monkeypatch):
    # patch DB methods used by /csv
    server.db.get_promo_id = lambda promo_str: 1

    def fake_generate_csv(promo_id, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("col\nvalue\n")
        return 1

    server.db.generate_csv = fake_generate_csv

    r = client.get("/api/csv", params={"promo_str": "Intranet"})
    assert r.status_code == 200
    assert "text/ics" in (r.headers.get("content-type") or "")  # ton code met text/ics (même si c'est un csv)
    assert "value" in r.text


def test_token_success(client, monkeypatch):
    monkeypatch.setattr(server, "authenticate_user", lambda u, p: True)
    monkeypatch.setattr(server, "create_access_token", lambda data: "FAKEJWT")

    r = client.post("/api/token", data={"username": "bob", "password": "secret"})
    assert r.status_code == 200
    assert r.json()["access_token"] == "FAKEJWT"
    assert r.json()["token_type"] == "bearer"


def test_token_failure(client, monkeypatch):
    monkeypatch.setattr(server, "authenticate_user", lambda u, p: False)
    r = client.post("/api/token", data={"username": "bob", "password": "wrong"})
    assert r.status_code == 401
