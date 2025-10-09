from fastapi.testclient import TestClient
from backend.server import app  # your FastAPI app
import pytest

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}

dummy_user_data = {
    "username":"brian",
    "email":"john.doe@gmail.com",
    "hashed_pwd":"sefs"
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
    "hashed_pwd":"rdgezgrbrg"
},
{
    "username":"sefsef",
    "email":"@gmail@gmail",             # double @
    "hashed_pwd":"sefsefsaizpvj2123"
},
{
    "username":"brian",
    "email":"john.doe@gmail.com",
    "hashed_pwd":""                     # no hashed pwd
}

]

def test_create_user():
    response = client.post("/create", json=dummy_user_data)
    assert response.is_success

    b = True
    for d in wrong_user_data:
        response = client.post("/create", json=d)
        if (response.is_success):   # response.is_success should always be False
            b = False
    
    assert b    # if b = True => all test successfully failed
    result = response.json()

