from typing import Annotated
from pydantic import BaseModel, field_validator, EmailStr
from fastapi import FastAPI, Depends, Query
from fastapi.security import OAuth2PasswordBearer
import sqlite3
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone


# ------- JWT --------
ACCESS_TOKEN_EXPIRES_MINUTES = 30
ALGORITHM = "HS256"
SECRET_KEY = "openssl09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"


class Token(BaseModel):
    access_token:str
    token_type:str

def create_access_token(data:dict, expires_delta:timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt   

# ----------------------

# custom imports : 'if' statement needed for unit tests
if __name__ == '__main__' or __name__=="server":
    from db_webcafe import WebCafeDB
else:
    from backend.db_webcafe import WebCafeDB


oauth2scheme = OAuth2PasswordBearer(tokenUrl="token")

# create FastAPI app
app = FastAPI()

db = WebCafeDB()

# define a request model for sending data (POST)
class User(BaseModel):
    login: Annotated[str, Query(min_length=1, max_length=20)]
    email:Annotated[EmailStr, Query(max_length=50)]
    nom:Annotated[str, Query(max_length=30)]
    prenom:Annotated[str, Query(max_length=30)]
    hpwd:Annotated[str, Query(max_length=100)]
    # birthdate
    superuser:bool | None = False
    owner:bool | None = False
    noteKfet:Annotated[str, Query(default="NoteDefault", max_length=30)]
    

class UserPassword(BaseModel):
    login: Annotated[str, Query(min_length=1, max_length=20)]
    hpwd: Annotated[str, Query(max_length=100)]

class Event(BaseModel):
    pass

class Calendar(BaseModel):
    pass


@app.post("/users/create")
async def create_user(user:User):
    """automaticaly parses User, if format ok, then adds user in db if possible"""
    db.conn = sqlite3.connect(db.dbname)
    res = db.insertUser(user.login, user.nom, user.prenom, user.hpwd, user.email,
                   superuser=user.superuser, owner=user.owner, noteKfet=user.noteKfet)
    db.conn.close()
    return res

@app.post("/users/login")
async def check_user(u_pwd:UserPassword):
    try:
        db.conn = sqlite3.connect(db.dbname)
        res = db.userCheckPassword(u_pwd.login, u_pwd.hpwd)
        db.conn.close()
        if res == -1:  
            return "wrong login/password"
        if res == -2:
            return "user does not exist"
        # res == 0
        return "good login/pwd" #TODO: JWT
    except:
        return "could not acces database"

@app.get("/")
async def read_root():
    return {"message":"Hello, World!"}
