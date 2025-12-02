import os
import sqlite3
import pytest
from backend.db_webcafe import WebCafeDB, convertPromoStrToInt

"""
1 : success
0 : not found
-1 : failure (e.g., duplicate entry, invalid input)
-2 : database connection error
"""
def setup_db_file(tmp_path):
    db_path = str(tmp_path / "test_webcafe.db")
    db = WebCafeDB(dbname=db_path)
    # reopen a connection for operations (WebCafeDB.__init__ closes its connection)
    db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
    return db

def test_convertPromoStrToInt_known_and_unknown():
    assert convertPromoStrToInt("Intranet") == 1
    assert convertPromoStrToInt("M1 E3A") == 2
    assert convertPromoStrToInt("PSEE") == 3
    assert convertPromoStrToInt("Saphire") == 4
    # unknown promo returns 0 (default)
    assert convertPromoStrToInt("DoesNotExist") == 0



def test_insert_user(tmp_path):
    db = setup_db_file(tmp_path) 
    # insert user: signature (login, nom, prenom, hpwd, email, birthday, promo_str, teacher, superuser, noteKfet)
    res = db.insertUser("alice", "Doe", "Alice", "securehash", "alice@example.com", "2000-01-01", "M1 E3A", False, True)
    assert res == 1

    # verify row in database
    cur = db.conn.cursor()
    row = cur.execute(
        "SELECT login, email, nom, prenom, hpwd, birthday, promo_id, teacher, superuser, noteKfet FROM users WHERE login = ?",
        ("alice",)
    ).fetchone()
    assert row is not None

    # expected values based on insert order and conversions:
    # login, email, nom, prenom, hpwd, birthday, promo_id (M1 E3A -> 2), teacher (False -> 0), superuser (True -> 1), noteKfet (default empty)
    assert row == ("alice", "alice@example.com", "Doe", "Alice", "securehash", "2000-01-01", 2, 0, 1, "")
    # inserting same login again should fail with -1
    res_dup = db.insertUser("alice", "Doe", "Alice", "securehash", "alice@example.com", "2000-01-01", "M1 E3A", False, True)
    assert res_dup == -1
    db.conn.close()
    # Attempt to insert user should return -2 due to closed connection
    res = db.insertUser("bob", "Smith", "Bob", "hash", "bob@example.com", "1990-05-15", "PSEE", False, False)
    assert res == -2

def test_deleteUser(tmp_path):
    db = setup_db_file(tmp_path)

    # insert a user to delete
    db.insertUser("charlie", "Brown", "Charlie", "hashcharlie", "charlie@example.com", "1985-07-20", "Intranet", False, False)
    res = db.deleteUser("charlie")

    assert res == 1
    assert not db._userExists("charlie")

    res_nonexistent = db.deleteUser("nonexistent")
    assert res_nonexistent == 0
    db.conn.close()
    res = db.deleteUser("anyuser")
    assert res == -2
 
def test_userExists(tmp_path):
    db = setup_db_file(tmp_path)

    # insert a user to check existence
    db.insertUser("dave", "Clark", "Dave", "hashdave", "dave@example.com", "1992-03-10", "Saphire", True, False)
    res = db._userExists("dave")
    assert res == 1
    res_nonexistent = db._userExists("eve")
    assert res_nonexistent == 0
    db.conn.close()
    res = db._userExists("dave")
    assert res == -2

def test_userCheckPassword(tmp_path):
    db = setup_db_file(tmp_path)

    # insert a user to check password
    db.insertUser("frank", "Wright", "Frank", "hashfrank", "frank@example.com", "1988-11-30", "M1 E3A", False, True)
    res = db.userCheckPassword("frank", "hashfrank")
    assert res == 1
    res_wrong = db.userCheckPassword("frank", "wronghash")
    assert res_wrong == -1
    res_nonexistent = db.userCheckPassword("ghost", "anyhash")
    assert res_nonexistent == 0
    db.conn.close()
    res_closed = db.userCheckPassword("frank", "hashfrank")
    assert res_closed == -2

def test_get_user(tmp_path):
    db = setup_db_file(tmp_path)
    # insert a user to retrieve
    db.insertUser("grace", "Hopper", "Grace", "hashgrace", "grace@example.com", "1906-12-09", "Intranet", True, True)
    user_info = db.get_user("grace")
    assert user_info is not None
    assert user_info["login"] == "grace"
    assert user_info["email"] == "grace@example.com"
    assert user_info["nom"] == "Hopper"
    assert user_info["prenom"] == "Grace"
    assert user_info["birthday"] == "1906-12-09"
    assert user_info["promo_id"] == "Intranet"
    assert user_info["teacher"] is True
    assert user_info["superuser"] is True
    assert user_info["noteKfet"] == ""
    res = db.get_user("nonexistent")
    assert res == 0
    db.conn.close()
    res = db.get_user("grace")
    assert res == -2

def test_user_getall(tmp_path):
    db = setup_db_file(tmp_path)
    res = db.user_getall()
    assert res == 0  # no users yet
    # insert multiple users
    db.insertUser("henry", "Ford", "Henry", "hashhenry", "henry@example.com", "1863-07-30", "PSEE", False, False)
    db.insertUser("isabel", "Allende", "Isabel", "hashisabel", "isabel@example.com", "1942-08-02", "Saphire", True, False)
    users = db.user_getall()
    assert isinstance(users, dict)
    assert "henry" in users
    assert "isabel" in users
    assert users["henry"]["email"] == "henry@example.com"
    assert users["henry"]["teacher"] is False
    assert users["henry"]["superuser"] is False
    assert users["henry"]["nom"] == "Ford"
    assert users["henry"]["prenom"] == "Henry"
    assert users["henry"]["promo_id"] == "PSEE" 
    assert users["isabel"]["email"] == "isabel@example.com"
    assert users["isabel"]["teacher"] is True
    assert users["isabel"]["superuser"] is False
    assert users["isabel"]["nom"] == "Allende"
    assert users["isabel"]["prenom"] == "Isabel"
    assert users["isabel"]["promo_id"] == "Saphire" 
    db.conn.close()
    res = db.user_getall()
    assert res == -2

def test_user_modify(tmp_path):
    db = setup_db_file(tmp_path)

    # insert a user to modify
    db.insertUser("jack", "London", "Jack", "hashjack", "jack@example.com", "1876-01-12", "M1 E3A", False, False)
    # modify some fields
    res = db.user_modify("jack", {"nom": "Smith", "prenom": "John", "promo_id": "PSEE", "birthday": "1876-01-15", "noteKfet": "Loves coffee"})
    assert res == 1
    user_info = db.get_user("jack")
    assert user_info["nom"] == "Smith"
    assert user_info["prenom"] == "John"
    assert user_info["promo_id"] == "PSEE"
    assert user_info["birthday"] == "1876-01-15"
    assert user_info["noteKfet"] == "Loves coffee"
    # attempt to modify with invalid keys
    res_invalid = db.user_modify("jack", {"invalid_key": "value"})
    assert res_invalid == -1
    # attempt to modify non-existent user
    res_nonexistent = db.user_modify("nonexistent", {"nom": "Noone"})
    assert res_nonexistent == 0
    # attempt to modify with empty dict
    res_empty = db.user_modify("jack", {})
    assert res_empty == -1
    res_wrong_promo = db.user_modify("jack", {"promo_id": "UnknownPromo"})
    assert res_wrong_promo == -1
    db.conn.close()
    res_closed = db.user_modify("jack", {"nom": "Closed"})
    assert res_closed == -2

def test_check_superuser(tmp_path):
    db = setup_db_file(tmp_path)

    # insert users
    db.insertUser("kate", "Winslet", "Kate", "hashkate", "kate@example.com", "1975-10-05", "Intranet", False, True)
    db.insertUser("leo", "DiCaprio", "Leo", "hashleo", "leo@example.com", "1974-11-11", "Intranet", False, False)
    res_kate = db.check_superuser("kate")
    assert res_kate == 1
    res_leo = db.check_superuser("leo")
    assert res_leo == -1
    res_nonexistent = db.check_superuser("nonexistent")
    assert res_nonexistent == 0
    db.conn.close()
    res_closed = db.check_superuser("kate")
    assert res_closed == -2

def test_set_Teacher(tmp_path):
    db = setup_db_file(tmp_path)
    # insert a user to set as teacher
    db.insertUser("mike", "Tyson", "Mike", "hashmike", "mike@example.com", "1966-06-30", "M1 E3A", False, False)
    res = db.set_Teacher("mike")
    assert res == 1
    user_info = db.get_user("mike")
    assert user_info["teacher"] is True
    # attempt to set non-existent user as teacher
    res_nonexistent = db.set_Teacher("nonexistent")
    assert res_nonexistent == 0
    db.conn.close()
    res_closed = db.set_Teacher("mike")
    assert res_closed == -2

def test_eventExists(tmp_path):
    db = setup_db_file(tmp_path)

    # insert an event to check existence
    db.insertEvent("2024-10-01 10:00", "2024-10-01 12:00", "Math", "Lecture", classroom_id=1, user_id=1, promo_id=2)
    res = db._eventExists("2024-10-01 10:00", 2)
    assert res == 1
    res_nonexistent = db._eventExists("0000-00-00 00:00", 10)
    assert res_nonexistent == 0
    db.conn.close()
    res_closed = db._eventExists("2024-10-01 10:00", 2)
    assert res_closed == -2

def test_insertEvent(tmp_path):
    db = setup_db_file(tmp_path)

    # insert an event
    res = db.insertEvent("2024-09-15 14:00", "2024-09-15 16:00", "Physics", "Seminar",infos_sup="Important details", classroom_id=2, user_id=1, promo_id=3)
    assert res == 1

    # verify row in database
    cur = db.conn.cursor()
    row = cur.execute(
        "SELECT start, end, matiere, type_cours, infos_sup, classroom_id, user_id, promo_id FROM events WHERE event_id = ?",
        (res,)).fetchone()
    assert row is not None
    assert row == ("2024-09-15 14:00", "2024-09-15 16:00", "Physics", "Seminar", "Important details", 2, 1, 3)
    # inserting same event again should fail with -1
    res_dup = db.insertEvent("2024-09-15 14:00", "2024-09-15 16:00", "Physics", "Seminar",infos_sup="Important details", classroom_id=2, user_id=1, promo_id=3)
    assert res_dup == -1

    db.conn.close()
    res_closed = db.insertEvent("2024-10-01 10:00", "2024-10-01 12:00", "Math", "Lecture", infos_sup=None, classroom_id=1, user_id=1, promo_id=2)
    assert res_closed == -2

def test_get_events_id(tmp_path):
    db = setup_db_file(tmp_path)
    


