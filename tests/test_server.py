import pytest
from fastapi.testclient import TestClient
from backend.server import app, create_access_token, User, UserPassword, Token
from datetime import timedelta, datetime, timezone
import backend.server as server_mod
import jwt

client = TestClient(app)


def test_create_access_token_and_decode():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    decoded = jwt.decode(token, server_mod.SECRET_KEY, algorithms=[server_mod.ALGORITHM])
    assert decoded["sub"] == "testuser"
    assert "exp" in decoded

def test_create_user_success():

    user_data = {
        "login": "newuser",
        "email": "newuser@example.com",
        "nom": "Nom",
        "prenom": "Prenom",
        "hpwd": "password",
        "birthday": "2000-01-01",
        "promo_id": "",
        "teacher": False,
        "superuser": False,
        "noteKfet": "NoteDefault"
    }
    response = client.post("/users/create", json=user_data)
    assert response.status_code == 201
    assert response.json()["message"] == "User succesfully created"

def test_create_user_conflict():
    user_data = {
        "login": "conflictuser",
        "email": "conflictuser@example.com",
        "nom": "Nom",
        "prenom": "Prenom",
        "hpwd": "password",
        "birthday": "2000-01-01",
        "promo_id": "",
        "teacher": False,
        "superuser": False,
        "noteKfet": "NoteDefault"
    }
    # First creation
    client.post("/users/create", json=user_data)
    # Second creation should fail
    response = client.post("/users/create", json=user_data)
    assert response.status_code == 409

def test_check_user_success():
    # Create user first
    server_mod.db.insertUser("loginuser", "Nom", "Prenom", "pwd", "loginuser@example.com", "", False, False, "NoteDefault", "2000-01-01")
    data = {"login": "loginuser", "hpwd": "pwd"}
    response = client.post("/users/login", json=data)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_check_user_wrong_password():
    server_mod.db.insertUser("wrongpwduser", "Nom", "Prenom", "pwd", "wrongpwduser@example.com", "", False, False, "NoteDefault", "2000-01-01")
    data = {"login": "wrongpwduser", "hpwd": "badpwd"}
    response = client.post("/users/login", json=data)
    assert response.status_code == 401

def test_get_my_info():
    server_mod.db.insertUser("info_user", "Nom", "Prenom", "pwd", "info_user@example.com", "", False, False, "NoteDefault", "2000-01-01")
    token = create_access_token({"sub": "info_user"})
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["login"] == "info_user"

def test_modify_my_data_success():
    server_mod.db.insertUser("moduser", "Nom", "Prenom", "pwd", "moduser@example.com", "", False, False, "NoteDefault", "2000-01-01")
    token = create_access_token({"sub": "moduser"})
    headers = {"Authorization": f"Bearer {token}"}
    data = {"nom": "NewNom"}
    response = client.post("/users/modify", headers=headers, json=data)
    assert response.status_code == 202

def test_modify_my_data_empty():
    server_mod.db.insertUser("modempty", "Nom", "Prenom", "pwd", "modempty@example.com", "", False, False, "NoteDefault", "2000-01-01")
    token = create_access_token({"sub": "modempty"})
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/users/modify", headers=headers, json={})
    assert response.status_code == 406

def test_set_use_teacher_superuser():
    server_mod.db.insertUser("superuser", "Nom", "Prenom", "pwd", "superuser@example.com", "", True, False, "NoteDefault", "2000-01-01")
    server_mod.db.insertUser("teachuser", "Nom", "Prenom", "pwd", "teachuser@example.com", "", False, False, "NoteDefault", "2000-01-01")
    token = create_access_token({"sub": "superuser"})
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/rights/set/teacher", headers=headers, params={"new_teacher_login": "teachuser"})
    assert response.status_code == 200

def test_set_use_teacher_not_superuser():
    server_mod.db.insertUser("not_super", "Nom", "Prenom", "pwd", "not_super@example.com", "", False, False, "NoteDefault", "2000-01-01")
    token = create_access_token({"sub": "not_super"})
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/rights/set/teacher", headers=headers, params={"new_teacher_login": "teachuser"})
    assert response.status_code == 401

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to the webcafe server"