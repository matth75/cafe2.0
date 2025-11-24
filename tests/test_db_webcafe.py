import os
import sys
import tempfile
import sqlite3
import importlib
import types
import pytest

# Provide a minimal fake icalendar module so importing db_webcafe in environments
# without the real icalendar package still works.
fake_ical = types.ModuleType("icalendar")


class FakeEvent:
    def __init__(self):
        self.props = {}

    def add(self, k, v):
        self.props[k] = v


class FakeCalendar:
    def __init__(self):
        self.components = []

    def add(self, k, v):
        # no-op for product/version
        pass

    def add_component(self, comp):
        self.components.append(comp)

    def to_ical(self):
        # return deterministic bytes so tests can assert output
        return b"BEGIN:VCALENDAR\nEND:VCALENDAR\n"


fake_ical.Calendar = FakeCalendar
fake_ical.Event = FakeEvent

# Insert fake module before importing the target module
sys.modules.setdefault("icalendar", fake_ical)

# Now import the module under test
db_mod = importlib.import_module("backend.db_webcafe")
WebCafeDB = db_mod.WebCafeDB


def make_temp_db():
    tf = tempfile.NamedTemporaryFile(delete=False)
    tf.close()
    return tf.name


def open_conn(dbpath):
    return sqlite3.connect(dbpath, check_same_thread=False)


def test_insert_user_and_password_checks_and_duplicates():
    dbpath = make_temp_db()
    try:
        db = WebCafeDB(dbname=dbpath)
        # reopen connection for operations (the class __init__ closes it)
        db.conn = open_conn(dbpath)

        res = db.insertUser(
            login="alice",
            nom="AliceNom",
            prenom="AlicePrenom",
            hpwd="hashpwd",
            email="alice@example.com",
            birthday="2000-01-01",
            promo_str="M1 E3A",
            teacher=False,
            superuser=False,
            noteKfet="note",
        )
        assert res == 1

        # duplicate insert should return -1
        res_dup = db.insertUser(
            login="alice",
            nom="X",
            prenom="Y",
            hpwd="h",
            email="a@b.c",
        )
        assert res_dup == -1

        # correct password
        assert db.userCheckPassword("alice", "hashpwd") == 0
        # wrong password
        assert db.userCheckPassword("alice", "bad") == -1
        # non-existent user
        assert db.userCheckPassword("noone", "any") == -2

        db.conn.close()
    finally:
        os.unlink(dbpath)


def test_get_user_getall_modify_and_set_teacher_and_superuser_check():
    dbpath = make_temp_db()
    try:
        db = WebCafeDB(dbname=dbpath)
        db.conn = open_conn(dbpath)

        # insert bob with promo PSEE (exists in mapping)
        rc = db.insertUser(
            login="bob",
            nom="BobNom",
            prenom="BobPrenom",
            hpwd="bobhash",
            email="bob@example.com",
            promo_str="PSEE",
        )
        assert rc == 1

        user = db.get_user("bob")
        assert isinstance(user, dict)
        assert user["login"] == "bob"
        assert user["promo_id"] == "PSEE"
        assert user["teacher"] is False
        assert user["superuser"] is False

        all_users = db.user_getall()
        assert "bob" in all_users
        assert all_users["bob"]["email"] == "bob@example.com"

        # modify bob promo to Saphire and name
        mod = db.user_modify("bob", {"nom": "BobNew", "promo_id": "Saphire"})
        assert mod == 1
        user2 = db.get_user("bob")
        assert user2["nom"] == "BobNew"
        assert user2["promo_id"] == "Saphire"

        # set teacher
        st = db.set_Teacher("bob")
        assert st == 1
        # check that teacher flag changed in get_user result
        user3 = db.get_user("bob")
        assert user3["teacher"] is True

        # check_superuser returns -1 for non-superuser
        assert db.check_superuser("bob") == -1

        db.conn.close()
    finally:
        os.unlink(dbpath)


def test_insert_event_fails_due_to_broken_query_and_event_exists_check():
    dbpath = make_temp_db()
    try:
        db = WebCafeDB(dbname=dbpath)
        db.conn = open_conn(dbpath)

        # insertEvent is implemented with a broken INSERT (mismatched placeholders),
        # it should return -2 on failure.
        res = db.insertEvent(
            start="2025-11-04 10:00",
            end="2025-11-04 12:00",
            matiere="Math",
            type_cours="CM",
            classroom_id=1,
            user_id=1,
            promo_id=2,
        )
        assert res == -2

        # _eventExists should return False for a non-existing event
        assert db._eventExists("2025-11-04 10:00", 2) is False

        db.conn.close()
    finally:
        os.unlink(dbpath)


def test_generate_ics_no_events_and_with_events():
    dbpath = make_temp_db()
    outpath = make_temp_db()
    try:
        db = WebCafeDB(dbname=dbpath)
        # create a connection to insert a raw event row (bypassing broken insertEvent)
        conn = open_conn(dbpath)
        cur = conn.cursor()
        # Insert a row with non-ISO datetime format to trigger the alternate parser branch
        cur.execute(
            "INSERT INTO events (start, end, matiere, type_cours, infos_sup, classroom_id, user_id, promo_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("2025-11-04 10:00", "2025-11-04 12:00", "Physics", "CM", "", 2, 5, 2),
        )
        conn.commit()
        conn.close()

        # generate_ics filtered by promo_id that matches -> should create file
        ret = db.generate_ics(db_name=dbpath, output_file=outpath, promo_id=2)
        assert ret == 1
        assert os.path.exists(outpath)
        with open(outpath, "rb") as f:
            data = f.read()
        assert b"BEGIN:VCALENDAR" in data

        # generate_ics with a filter that matches no events should return -1
        out2 = make_temp_db()
        try:
            no_events_ret = db.generate_ics(db_name=dbpath, output_file=out2, promo_id=9999)
            assert no_events_ret == -1
            # ensure no file created/empty
            if os.path.exists(out2):
                # If file was created, it should be empty or not a valid calendar from our fake
                with open(out2, "rb") as f:
                    content = f.read()
                assert content == b"" or b"BEGIN:VCALENDAR" not in content
        finally:
            if os.path.exists(out2):
                os.unlink(out2)

    finally:
        if os.path.exists(dbpath):
            os.unlink(dbpath)
        if os.path.exists(outpath):
            os.unlink(outpath)

