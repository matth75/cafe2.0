from fastapi.testclient import TestClient
from backend.server import app  # your FastAPI app
from backend.db_webcafe import WebCafeDB
import pytest

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}

dummy_user_data = {
    "login":"mrouet",
    "nom":"Matth",
    "prenom":"ROUUU",
    "superuser":True,
    "email":"my.email@gmail.com",
    "hpwd":"xdfsdfefbdgrzbeag1234"
}

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
    test_state = True
    dbname = "whatAStupid.db"
    db = WebCafeDB(dbname)
    test_state = db.insertUser( "wowawiwo", "name", "prename", "azezgfbez", "email@email.com", birthdate="2003-12-7", owner=True)
    test_state = db.insertUser( "hello4", "name", "wow", "azezgfbez", "fef@email.com", noteKfet="hfesf")
    db.deleteUser('users', login="hello")
    return test_state
    
    