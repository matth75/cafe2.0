from fastapi.testclient import TestClient
from backend.server import app, create_access_token  # your FastAPI app
from backend.db_webcafe import WebCafeDB
import pytest
import sqlite3

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

user_data_to_check = [dummy_user_data, dummy_user_data2]

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

def test_create_user():
    response = client.post("/users/create", json=dummy_user_data)
    assert response.is_success

    b = True
    for d in wrong_user_data:
        response = client.post("/users/create", json=d)
        if (response.is_success):   # response.is_success should always be False
            b = False
    
    assert b    # if b = True => all test successfully failed
    result = response.json()


def test_insertUserDB():
    dbname = "whatAStupid.db"
    db = WebCafeDB(dbname)
    db.conn = sqlite3.connect(db.dbname)
    db.insertUser( "wosef", "name", "prename", "azezgfbez", "email@email.com", birthdate="2003-12-7", owner=True)
    db.insertUser( "hello4", "name", "wow", "azezgfbez", "fef@email.com", noteKfet="hfesf")
    db.deleteUser('users', login="hello")
    db.conn.close()
    

def test_checkUser():
    dbname = "whatAStupid.db"
    db = WebCafeDB(dbname)
    db.conn = sqlite3.connect(db.dbname)
    db.insertUser( "007", "name", "prename", "mypwdtouse", "email@email.com", birthdate="2003-12-7", owner=True)
    assert db.userCheckPassword("007", "mypwdtouse") == 0
    db.conn.close()

def test_extensiveCheckUser():
    db = WebCafeDB(dbname)
    db.conn = sqlite3.connect(db.dbname)
    for j in user_data_to_check:
        db.insertUser(login=j["login"], nom=j["nom"], prenom=j["prenom"], hpwd=j["hpwd"], email=j["email"])
        assert db.userCheckPassword(j["login"], j["hpwd"]) == 0
        user_info = db.get_user(j["login"])
        assert user_info["login"]==j["login"]


def test_createJWT():
    data = {"hello":"wow"}
    mydata = create_access_token(data)
    print("dummy text")


def test_getUser():
    db = WebCafeDB("whatAStupid.db")
    db.conn = sqlite3.connect("whatAStupid.db")
    db.insertUser("wowawiwo", "name", "prename", "mypwdtouse", "email@email.com", birthdate="2003-12-7", superuser=True, owner=True)
    res = db.get_user("wowawiwo")
    assert res["login"] ==  "wowawiwo"
    assert res["email"] == "email@email.com"
    db.conn.close()