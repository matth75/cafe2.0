from fastapi.testclient import TestClient
from backend.server import app, create_access_token  # your FastAPI app
from backend.db_webcafe import WebCafeDB
import pytest
import sqlite3
from datetime import datetime
client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message":"Welcome to the webcafe server"}

dbname = "whatAStupid.db"

dummy_user_data = {
    "login":"mrouet",
    "nom":"Matth",
    "prenom":"ROUUU",
    "superuser":True,
    "email":"my.email@gmail.com",
    "hpwd":"xdfsdfefbdgrzbeag1234"
}

dummy_user_data2 = {
    "login":"008",
    "nom":"sefes",
    "prenom":"007",
    "superuser":True,
    "email":"my.email@gmail.com",
    "hpwd":"xdfsdfefbdgrzbeag1234"
}

dummy_user_data3 = {
    "login":"user",
    "nom":"me",
    "prenom":"nothim",
    "superuser":True,
    "email":"my.email@gmail.com",
    "hpwd":"test"
}


user_data_to_check = [dummy_user_data, dummy_user_data2, dummy_user_data3]

wrong_user_data = [
{
    # empty field
},
{
    "username":""       # missing fields
},
{
    "username":"azerhgjghdsfdazefrg",    # too long
    "email":"sefsg",
    "hpwd":"rdgezgrbrg"
},
{
    "username":"sefsef",
    "email":"@gmail@gmail",             # double @
    "hpwd":"sefsefsaizpvj2123"
},
{
    "username":"brian",
    "email":"john.doe@gmail.com",
    "hpwd":""                     # no hashed pwd
}

]

# def test_create_user():
#     response = client.post("/users/create", json=dummy_user_data)
#     assert response.is_success

#     b = True
#     for d in wrong_user_data:
#         response = client.post("/users/create", json=d)
#         if (response.is_success):   # response.is_success should always be False
#             b = False
    
#     assert b    # if b = True => all test successfully failed
#     result = response.json()


def test_insertUserDB():
    dbname = "whatAStupid.db"
    db = WebCafeDB(dbname)
    db.conn = sqlite3.connect(db.dbname)
    db.insertUser( login="wosef", nom="name", prenom="prename", hpwd="azezgfbez", email="email@email.com", birthday="2003-12-7", teacher=True)
    db.insertUser( login="hello4", nom="name", prenom="wow", hpwd="azezgfbez", email="fef@email.com", noteKfet="hfesf")
    db.deleteUser('users', login="hello")
    db.conn.close()
    

def test_checkUser():
    dbname = "whatAStupid.db"
    db = WebCafeDB(dbname)
    db.conn = sqlite3.connect(db.dbname)
    db.insertUser(login="007", nom="name", prenom="prename", hpwd="mypwdtouse", email="email@email.com", birthday="2003-12-7", superuser=True)
    assert db.userCheckPassword("007", "mypwdtouse") == 0
    db.conn.close()

def test_extensiveCheckUser():
    db = WebCafeDB(dbname)
    db.conn = sqlite3.connect(db.dbname)
    for j in user_data_to_check:
        db.insertUser(login=j["login"], nom=j["nom"], prenom=j["prenom"], hpwd=j["hpwd"], email=j["email"])
        assert db.userCheckPassword(j["login"], j["hpwd"]) == 0
        user_info = db.get_user(j["login"])
        assert user_info["login"]==j["login"]   #type: ignore


def test_createJWT():
    data = {"hello":"wow"}
    mydata = create_access_token(data)
    print("dummy text")


def test_getUser():
    db = WebCafeDB("whatAStupid.db")
    db.conn = sqlite3.connect("whatAStupid.db")
    db.insertUser(login="wowawiwo", nom="name", prenom="prename", hpwd="mypwdtouse", email="email@email.com", birthday="2003-12-7", superuser=True, teacher=True)
    res = db.get_user("wowawiwo")
    assert res["login"] ==  "wowawiwo"   #type: ignore
    assert res["email"] == "email@email.com"     #type: ignore
    res = db.get_user("user")
    db.conn.close()


def test_setTeacher():
    db = WebCafeDB("whatAStupid.db")
    db.conn = sqlite3.connect("whatAStupid.db")
    db.insertUser(login="myman", nom="name", prenom="prename", hpwd="mypwdtouse", email="email@email.com", birthday="2003-12-7", superuser=True, teacher=True)
    db.insertUser(login="trythis", nom="bebe", prenom="fefe", hpwd="again?", email="yolo@email.com", birthday="2043-12-7", superuser=False, teacher=False)
    res = db.check_superuser("myman")
    assert res == 1
    res = db.set_Teacher("trythis")
    assert res == 1
    db.conn.close()


new_data = [
    {"promo_id": 23},
    {"promo_id": '23'},
    {"nom": "leonard", "birthday":"1704-10-10"}
]

new_wrong_data = [
    {},
    {"wrongkey":""},
    {"login":"newlogin?!"},
    {"teacher":False},
    {"email":"anotherone@email.com"}
]

def test_modify_info():
    db = WebCafeDB("whatAStupid.db")
    db.conn = sqlite3.connect("whatAStupid.db")
    db.insertUser(login="graal", nom="king", prenom="arthur", hpwd="excalibur", email="oldman@email.com", birthday="1703-12-28", superuser=False, teacher=True)
    for d in new_data:
        assert db.user_modify("graal", d) == 1
    for d in new_wrong_data:
        res = db.user_modify("graal", d)
        assert  res == -1 or res == -3  # no data or invalid keys
    db.conn.close()


def test_users_get_all():
    db = WebCafeDB("whatAStupid.db")
    db.conn = sqlite3.connect("whatAStupid.db")
    db.user_getall()
    db.conn.close()


def test_generate_ics():
    db = WebCafeDB("webcafe.db")
    db.generate_ics(db_name=db.dbname, output_file="wow.ics", classroom_id=1, user_id=1, promo_id=1)


def test_get_events_id():
    db = WebCafeDB("webcafe.db")
    db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
    res = db._get_events_id({"classroom_id":1, "user_id":1, "promo_id":1})
    assert isinstance(res, list)
    res = db._get_events_id({"start":datetime(2025,12,5,8,0)})
    assert res != -1
    db.conn.close()