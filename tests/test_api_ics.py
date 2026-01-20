# tests/test_api_ics.py
import os
import json
import backend.routers.ics as ics_router


def test_ics_get_all_generates_file(client, monkeypatch):
    # generate_ics écrit un fichier .ics minimal
    def fake_generate_ics(db_name, output_file, **kwargs):
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("BEGIN:VCALENDAR\nEND:VCALENDAR\n")
        return 1

    monkeypatch.setattr(ics_router.db, "generate_ics", fake_generate_ics)

    r = client.get("/api/ics/get_all")
    assert r.status_code == 200
    assert "BEGIN:VCALENDAR" in r.text


def test_ics_insert_event_ok(client, monkeypatch):
    monkeypatch.setattr(ics_router, "elevated_rights", lambda user: True)
    monkeypatch.setattr(ics_router.db, "get_classroom_id", lambda s: 1)
    monkeypatch.setattr(ics_router.db, "get_promo_id", lambda s: 1)
    monkeypatch.setattr(ics_router.db, "insertEvent", lambda **kwargs: 1)

    payload = {
        "start": "2026-01-20T10:00:00",
        "end": "2026-01-20T12:00:00",
        "matiere": "Maths",
        "type_cours": "CM",
        "infos_sup": "",
        "classroom_str": "2Z34",
        "user_id": 0,
        "promo_str": "Intranet",
    }

    r = client.post("/api/ics/insert", json=payload)
    assert r.status_code == 200


def test_ics_insert_event_forbidden(client, monkeypatch):
    monkeypatch.setattr(ics_router, "elevated_rights", lambda user: False)

    payload = {
        "start": "2026-01-20T10:00:00",
        "end": "2026-01-20T12:00:00",
        "matiere": "Maths",
        "type_cours": "CM",
        "infos_sup": "",
        "classroom_str": "2Z34",
        "user_id": 0,
        "promo_str": "Intranet",
    }

    r = client.post("/api/ics/insert", json=payload)
    assert r.status_code == 401


def test_ics_event_filter_returns_list(client, monkeypatch):
    monkeypatch.setattr(ics_router.db, "_get_events_id", lambda criteria: [1, 2])
    monkeypatch.setattr(ics_router.db, "_get_events_on_ids", lambda ids: [{"event_id": 1}, {"event_id": 2}])

    r = client.get("/api/ics/event_filter", params={"matiere": "Maths"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) == 2


def test_ics_insert_classroom_ok(client, monkeypatch):
    monkeypatch.setattr(ics_router, "elevated_rights", lambda user: True)
    monkeypatch.setattr(ics_router.db, "insertClassroom", lambda **kwargs: 1)

    payload = {"capacity": 30, "type": "TP", "location": "2Z99"}
    r = client.post("/api/ics/insert_classroom", json=payload)
    assert r.status_code == 200
