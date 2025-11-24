import os
import sqlite3
import pytest
from backend.db_webcafe import WebCafeDB, convertPromoStrToInt

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
    conn = sqlite3.connect(db.dbname)
    cur = conn.cursor()
    row = cur.execute(
        "SELECT login, email, nom, prenom, hpwd, birthday, promo_id, teacher, superuser, noteKfet FROM users WHERE login = ?",
        ("alice",)
    ).fetchone()
    conn.close()

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
    assert db._userExists("dave") is True
    assert db._userExists("eve") is False
    db.conn.close()
    res = db._userExists("dave")
    assert res == -2

def test_userCheckPassword(tmp_path):
    
     

