# test_webcafedb.py
import sqlite3
import pytest
from datetime import datetime


from backend.db_webcafe import WebCafeDB, convertPromoStrToInt, load_inverse_promos



@pytest.fixture
def db(tmp_path):
    """
    Fixture: crée une base sqlite temporaire + initialise les tables via WebCafeDB.
    IMPORTANT: ton __init__ ferme self.conn, donc on la ré-ouvre pour les tests.
    """
    db_file = tmp_path / "test_webcafe.db"

    # Les fonctions globales se basent sur WebCafeDB.dbname -> on pointe dessus.
    WebCafeDB.dbname = str(db_file)

    # init (création tables + données par défaut)
    _ = WebCafeDB(dbname=str(db_file))

    # instance utilisable (connexion ouverte)
    instance = WebCafeDB(dbname=str(db_file))
    instance.conn = sqlite3.connect(str(db_file), check_same_thread=False)
    yield instance
    instance.conn.close()


# -------------------------
# Fonctions globales
# -------------------------

def test_convertPromoStrToInt_empty_returns_0(db):
    assert convertPromoStrToInt("") == 0
    assert convertPromoStrToInt(None) == 0  # type: ignore


def test_convertPromoStrToInt_existing_promo(db):
    # promos par défaut via _fill_promo(): ["Intranet", "M1_E3A", "PSEE", "Saphire"]
    pid = convertPromoStrToInt("M1_E3A")
    assert isinstance(pid, int)
    assert pid > 0


def test_convertPromoStrToInt_unknown_returns_0(db):
    assert convertPromoStrToInt("UNKNOWN_PROMO") == 0


def test_load_inverse_promos_contains_defaults(db):
    promos = load_inverse_promos()
    assert isinstance(promos, list)
    assert "M1_E3A" in promos


# -------------------------
# Users
# -------------------------

def test__userExists_unknown_returns_0(db):
    assert db._userExists("ghost") == 0


def test_insertUser_success(db):
    res = db.insertUser(
        login="alice",
        nom="Doe",
        prenom="Alice",
        hpwd="hash",
        email="alice@test.com",
        birthday="2000-01-01",
        promo_str="M1_E3A",
        teacher=False,
        superuser=False,
        noteKfet="hi",
    )
    assert res == 1
    assert db._userExists("alice") == 1


def test_insertUser_duplicate_returns_minus1(db):
    assert db.insertUser("bob", "N", "P", "h", "b@test.com") == 1
    assert db.insertUser("bob", "N", "P", "h", "b2@test.com") == -1


def test_userGetHashedPwd_ok(db):
    db.insertUser("carol", "N", "P", "secret_hash", "c@test.com")
    assert db.userGetHashedPwd("carol") == "secret_hash"


def test_userGetHashedPwd_unknown_returns_minus2(db):
    assert db.userGetHashedPwd("ghost") == -2


def test_get_user_unknown_returns_0(db):
    assert db.get_user("ghost") == 0


def test_get_user_ok_structure(db):
    db.insertUser("dave", "Nom", "Prenom", "h", "d@test.com", promo_str="PSEE", teacher=True, superuser=False)
    u = db.get_user("dave")
    assert isinstance(u, dict)
    assert u["login"] == "dave"
    assert u["promo_id"] in ("PSEE", "")  # promo name
    assert isinstance(u["teacher"], bool)
    assert isinstance(u["superuser"], bool)


def test_user_getall_returns_dict(db):
    db.insertUser("e1", "N", "P", "h", "e1@test.com", promo_str="M1_E3A", teacher=True, superuser=True)
    res = db.user_getall()
    assert isinstance(res, dict)
    assert "e1" in res
    assert "email" in res["e1"]


def test_user_modify_invalid_keys_returns_minus1(db):
    db.insertUser("emma", "N", "P", "h", "e@test.com")
    assert db.user_modify("emma", {"badkey": "x"}) == -1
    assert db.user_modify("emma", {}) == -1


def test_user_modify_user_not_found_returns_0(db):
    assert db.user_modify("ghost", {"nom": "X"}) == 0


def test_user_modify_ok(db):
    db.insertUser("frank", "Old", "P", "h", "f@test.com", promo_str="M1_E3A")
    assert db.user_modify("frank", {"nom": "NewNom", "promo_id": "PSEE"}) == 1
    u = db.get_user("frank")
    assert u["nom"] == "NewNom"
    assert u["promo_id"] == "PSEE"


def test_user_modify_invalid_promo_returns_minus1(db):
    db.insertUser("gina", "N", "P", "h", "g@test.com")
    assert db.user_modify("gina", {"promo_id": "DOES_NOT_EXIST"}) == -1


def test_check_superuser_paths(db):
    db.insertUser("su", "N", "P", "h", "su@test.com", superuser=True)
    db.insertUser("nosu", "N", "P", "h", "nosu@test.com", superuser=False)
    assert db.check_superuser("ghost") == 0
    assert db.check_superuser("su") == 1
    assert db.check_superuser("nosu") == -1


def test_check_teacher_paths(db):
    db.insertUser("t", "N", "P", "h", "t@test.com", teacher=True)
    db.insertUser("not", "N", "P", "h", "not@test.com", teacher=False)
    assert db.check_teacher("ghost") == 0
    assert db.check_teacher("t") == 1
    assert db.check_teacher("not") == -1


def test_set_teacher_and_remove_teacher(db):
    db.insertUser("tt", "N", "P", "h", "tt@test.com", teacher=False)
    assert db.set_teacher("tt") == 1
    assert db.check_teacher("tt") == 1
    assert db.remove_teacher("tt") == 1
    assert db.check_teacher("tt") == -1


def test_remove_user(db):
    db.insertUser("rm", "N", "P", "h", "rm@test.com")
    assert db.remove_user("rm") == 1
    assert db._userExists("rm") == 0


def test_deleteUser_by_login(db):
    db.insertUser("del", "N", "P", "h", "del@test.com")
    assert db.deleteUser("del") == 1
    assert db.deleteUser("del") == 0  # already gone


# -------------------------
# Datetime helper
# -------------------------

def test__norm_dt_datetime_to_iso(db):
    dt = datetime(2025, 1, 2, 3, 4)
    s = db._norm_dt(dt)
    assert s == "2025-01-02T03:04"


def test__norm_dt_passthrough(db):
    assert db._norm_dt("2025-01-02T03:04") == "2025-01-02T03:04"


# -------------------------
# Classroom
# -------------------------

def test_get_classroom_id_unknown_returns_minus3(db):
    assert db.get_classroom_id("NOPE") == -3


def test_insertClassroom_then_get_id(db):
    assert db.insertClassroom("X1", 42, "CM") == 1
    cid = db.get_classroom_id("X1")
    assert cid > 0


def test_insertClassroom_duplicate_returns_minus1(db):
    assert db.insertClassroom("X2", 30, "TP") == 1
    assert db.insertClassroom("X2", 30, "TP") == -1


def test_deleteClassroom_ok(db):
    db.insertClassroom("X3", 30, "TP")
    assert db.deleteClassroom("X3") == 1
    assert db.get_classroom_id("X3") == -3


def test_deleteClassroom_unknown_returns_minus1(db):
    assert db.deleteClassroom("NOPE") == -1


# -------------------------
# Events
# -------------------------

def test__eventExists_false(db):
    assert db._eventExists("2099-01-01T10:00", 1) in (False, 0)


def test_insertEvent_success(db):
    # besoin d'un classroom_id existant
    cid = db.get_classroom_id("2Z28")  # rempli par défaut via _fill_classroom()
    assert cid > 0

    start = datetime(2025, 11, 4, 10, 0)
    end = datetime(2025, 11, 4, 12, 0)
    res = db.insertEvent(start, end, "Math", "CM", classroom_id=cid, promo_id=1)
    assert res == 1


def test_insertEvent_duplicate_returns_minus1(db):
    cid = db.get_classroom_id("2Z28")
    start = datetime(2025, 11, 4, 10, 0)
    end = datetime(2025, 11, 4, 12, 0)
    assert db.insertEvent(start, end, "Math", "CM", classroom_id=cid, promo_id=1) == 1
    assert db.insertEvent(start, end, "Math", "CM", classroom_id=cid, promo_id=1) == -1


def test__get_events_id_single_and_multi(db):
    cid = db.get_classroom_id("2Z28")
    start = datetime(2025, 11, 4, 10, 0)
    end = datetime(2025, 11, 4, 12, 0)
    db.insertEvent(start, end, "Math", "CM", classroom_id=cid, promo_id=1)

    # single
    eid = db._get_events_id({"start": start.strftime("%Y-%m-%dT%H:%M"), "promo_id": 1}, single=True)
    assert isinstance(eid, int) and eid > 0

    # multi
    ids = db._get_events_id({"promo_id": 1}, single=False)
    assert isinstance(ids, list)
    assert eid in ids


def test__get_events_on_ids(db):
    cid = db.get_classroom_id("2Z28")
    start = datetime(2025, 11, 4, 10, 0)
    end = datetime(2025, 11, 4, 12, 0)
    db.insertEvent(start, end, "Math", "CM", classroom_id=cid, promo_id=1)

    eid = db._get_events_id({"promo_id": 1}, single=True)
    events = db._get_events_on_ids([eid])
    assert len(events) == 1
    assert events[0]["event_id"] == eid
    assert "classroom_location" in events[0]


def test_deleteEvent_invalid_id_returns_minus3(db):
    assert db.deleteEvent(0) == -3
    assert db.deleteEvent(-1) == -3


def test_deleteEvent_not_found_returns_minus1(db):
    assert db.deleteEvent(999999) == -1


def test_deleteEvent_ok(db):
    cid = db.get_classroom_id("2Z28")
    start = datetime(2025, 11, 4, 10, 0)
    end = datetime(2025, 11, 4, 12, 0)
    db.insertEvent(start, end, "Math", "CM", classroom_id=cid, promo_id=1)
    eid = db._get_events_id({"promo_id": 1}, single=True)

    assert db.deleteEvent(eid) == 1
    assert db.deleteEvent(eid) == -1


def test_modifyEvent_invalid_input_returns_minus1(db):
    assert db.modifyEvent(0, {"matiere": "X"}) == -1
    assert db.modifyEvent(1, {}) == -1
    assert db.modifyEvent(1, {"badkey": "X"}) == -1


def test_modifyEvent_not_found_returns_0(db):
    assert db.modifyEvent(999999, {"matiere": "X"}) == 0


def test_modifyEvent_ok(db):
    cid = db.get_classroom_id("2Z28")
    start = datetime(2025, 11, 4, 10, 0)
    end = datetime(2025, 11, 4, 12, 0)
    db.insertEvent(start, end, "Old", "CM", classroom_id=cid, promo_id=1)
    eid = db._get_events_id({"promo_id": 1}, single=True)

    assert db.modifyEvent(eid, {"matiere": "New"}) == 1
    ev = db._get_events_on_ids([eid])[0]
    assert ev["matiere"] == "New"



def test_isClassroomUsed_returns_minus1_if_classroom_unknown(db):
    start = datetime(2025, 11, 4, 10, 0)
    end = datetime(2025, 11, 4, 12, 0)
    assert db.isClassroomUsed("NO_SUCH_ROOM", start, end) == -1


def test_isClassroomUsed_false_when_no_event(db):
    start = datetime(2025, 11, 4, 10, 0)
    end = datetime(2025, 11, 4, 12, 0)
    assert db.isClassroomUsed("2Z28", start, end) is False


def test_isClassroomUsed_true_when_exact_overlap(db):
    cid = db.get_classroom_id("2Z28")
    start = datetime(2025, 11, 4, 10, 0)
    end = datetime(2025, 11, 4, 12, 0)

    assert db.insertEvent(start, end, "Math", "CM", classroom_id=cid, promo_id=1) == 1
    assert db.isClassroomUsed("2Z28", start, end) is True


def test_isClassroomUsed_true_when_partial_overlap_left(db):
    cid = db.get_classroom_id("2Z28")
    # event existant: 10:00 - 12:00
    db.insertEvent(datetime(2025, 11, 4, 10, 0), datetime(2025, 11, 4, 12, 0),
                   "Math", "CM", classroom_id=cid, promo_id=1)

    # requête: 09:00 - 10:30 (chevauche)
    assert db.isClassroomUsed("2Z28", datetime(2025, 11, 4, 9, 0), datetime(2025, 11, 4, 10, 30)) is True


def test_isClassroomUsed_true_when_partial_overlap_right(db):
    cid = db.get_classroom_id("2Z28")
    db.insertEvent(datetime(2025, 11, 4, 10, 0), datetime(2025, 11, 4, 12, 0),
                   "Math", "CM", classroom_id=cid, promo_id=1)

    # requête: 11:30 - 13:00 (chevauche)
    assert db.isClassroomUsed("2Z28", datetime(2025, 11, 4, 11, 30), datetime(2025, 11, 4, 13, 0)) is True


def test_isClassroomUsed_true_when_new_contains_existing(db):
    cid = db.get_classroom_id("2Z28")
    db.insertEvent(datetime(2025, 11, 4, 10, 0), datetime(2025, 11, 4, 12, 0),
                   "Math", "CM", classroom_id=cid, promo_id=1)

    # requête: 09:00 - 13:00 (englobe)
    assert db.isClassroomUsed("2Z28", datetime(2025, 11, 4, 9, 0), datetime(2025, 11, 4, 13, 0)) is True


def test_isClassroomUsed_false_when_touching_edge_only(db):
    cid = db.get_classroom_id("2Z28")
    db.insertEvent(datetime(2025, 11, 4, 10, 0), datetime(2025, 11, 4, 12, 0),
                   "Math", "CM", classroom_id=cid, promo_id=1)

    # requête: 12:00 - 13:00 (touche juste la fin, pas de chevauchement)
    assert db.isClassroomUsed("2Z28", datetime(2025, 11, 4, 12, 0), datetime(2025, 11, 4, 13, 0)) is False



# -------------------------
# Promo helper
# -------------------------

def test_get_promo_id_ok_and_unknown(db):
    assert db.get_promo_id("M1_E3A") > 0
    assert db.get_promo_id("UNKNOWN") == -1
