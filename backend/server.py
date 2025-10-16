from typing import Annotated
from pydantic import BaseModel, field_validator, EmailStr
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import sqlite3
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash


# ------- JWT --------
ACCESS_TOKEN_EXPIRES_MINUTES = 30
ALGORITHM = "HS256"
SECRET_KEY = "openssl09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

pwd_hash = PasswordHash.recommended()

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


oauth2scheme = OAuth2PasswordBearer(tokenUrl="token")   # url which it defaults to to lend JWT

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
    # try 10 times with wait if SQL base already used ?
    db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
    res = db.insertUser(user.login, user.nom, user.prenom, pwd_hash.hash(user.hpwd), user.email,
                   superuser=user.superuser, owner=user.owner, noteKfet=user.noteKfet)
    db.conn.close()
    return res

@app.post("/users/login")
async def check_user(u_pwd:UserPassword):
    try:
        db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
        res = db.userCheckPassword(u_pwd.login, u_pwd.hpwd)
        db.conn.close()
        if res == -1 or res == -2:  
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        # if res == -2:
        #     return "user does not exist"
        else:
            access_token = create_access_token(data={"sub":u_pwd.login})
        return Token(access_token=access_token, token_type='bearer') 
    except:
        return "could not acces database"


# ------- ICS management -------
class JsonCalendar():
    pass

# ---------Login management ---------

# def check_pwd(plain_pwd, hashed_pwd):
#     return pwd_hash.verify(plain_pwd, hashed_pwd)

# def get_pwd_hash(plain_pwd):
#     return pwd_hash.hash(plain_pwd)

class Token(BaseModel):
    access_token:str
    token_type:str

def authenticate_user(username, pwd):
    hpwd = pwd_hash.hash(pwd)
    try:
        db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
        res = db.userCheckPassword(username, hpwd)
        db.conn.close()
        if res == 0:
            return True   
    except:
        return False


@app.post("/token")
async def login(form_data:Annotated[OAuth2PasswordRequestForm, Depends()]):
    # login = form_data.username
    # hpwd = form_data.password
    try:
        db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
        res = db.userCheckPassword(form_data.username, form_data.password)
        db.conn.close()
    except:
        "db innaccessible"
    if res == -1 or res == -2:  
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # if res == -2:
    #     return "user does not exist"  
    else:
        access_token = create_access_token(data={"sub":form_data.username})
        return Token(access_token=access_token, token_type="bearer")




async def get_current_user(token: Annotated[str, Depends(oauth2scheme)]):
    # login = decode_token(token)
    # return login ()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login = payload.get("sub")
        if login is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    return login


dummyICS = ["icsM1", "icsM2"]
list_authorized_M1 = ["mylogin", "hello4"]

@app.get("/users/me")
async def get_my_info(current_user : Annotated[str, Depends(get_current_user)]):

    return current_user

@app.get("/ics/M2")
async def post_calendar(current_login : Annotated[str, Depends(get_current_user)]): 
    if (current_login in list_authorized_M1):
        return dummyICS[1]
    return "Access denied / not on the list"


@app.get("/")
async def read_root():
    return {"message":"Hello, World!"}
