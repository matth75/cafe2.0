# tests/conftest.py
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # /home/maths/cafe/cafe2.0
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import sqlite3
import pytest
from fastapi.testclient import TestClient

import backend.server as server
import backend.routers.users as users_router
import backend.routers.ics as ics_router
import backend.dependancies as deps


def _init_test_db(db_path: str):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # classroom
    c.execute("""
    CREATE TABLE IF NOT EXISTS classroom (
        classroom_id INTEGER PRIMARY KEY AUTOINCREMENT,
        location CHAR(20) UNIQUE,
        capacity INT,
        type CHAR(20)
    )""")
    c.execute("INSERT OR IGNORE INTO classroom (classroom_id, location, capacity, type) VALUES (1,'2Z34',30,'TP')")

    # promo
    c.execute("""
    CREATE TABLE IF NOT EXISTS promo (
        promo_id INTEGER PRIMARY KEY AUTOINCREMENT,
        promo_name TEXT UNIQUE
    )""")
    c.execute("INSERT OR IGNORE INTO promo (promo_id, promo_name) VALUES (1,'Intranet')")
    c.execute("INSERT OR IGNORE INTO promo (promo_id, promo_name) VALUES (2,'M1_E3A')")

    # users
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login CHAR(30),
        email CHAR(60),
        nom CHAR(30),
        prenom CHAR(30),
        hpwd TEXT,
        birthday DATE,
        promo_id INT,
        teacher BIT,
        superuser BIT,
        noteKfet CHAR(30)
    )""")

    # events
    c.execute("""
    CREATE TABLE IF NOT EXISTS events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        start DATETIME,
        end DATETIME,
        matiere CHAR(50),
        type_cours CHAR(50),
        infos_sup CHAR(200),
        classroom_id INT,
        user_id INT,
        promo_id INT
    )""")

    # meta
    c.execute("""
    CREATE TABLE IF NOT EXISTS meta (
        key TEXT PRIMARY KEY,
        version INTEGER DEFAULT 0,
        last_modified TEXT DEFAULT (datetime('now'))
    )""")
    c.execute("INSERT OR IGNORE INTO meta (key, version) VALUES ('events', 0)")

    conn.commit()
    conn.close()


@pytest.fixture()
def app_and_db(tmp_path, monkeypatch):
    # isolate filesystem side-effects in temp dir
    monkeypatch.chdir(tmp_path)

    db_path = str(tmp_path / "test_webcafe.db")
    _init_test_db(db_path)

    # point all modules to the test DB
    server.db.dbname = db_path
    users_router.db.dbname = db_path
    ics_router.db.dbname = db_path
    deps.db.dbname = db_path

    # isolate CSV and ICS folders
    monkeypatch.setattr(server, "CSV_ROOT_PATH", "csv")
    monkeypatch.setattr(ics_router, "ICS_ROOT_PATH", "ics")

    # override auth dependency: no need for real JWT in unit tests
    async def fake_current_user():
        return "admin"

    server.app.dependency_overrides[deps.get_current_user] = fake_current_user

    # elevated rights: default True (override per-test if needed)
    monkeypatch.setattr(deps, "elevated_rights", lambda user: True)
    monkeypatch.setattr(ics_router, "elevated_rights", lambda user: True)

    return server.app, db_path


@pytest.fixture()
def client(app_and_db):
    app, _ = app_and_db
    return TestClient(app)
