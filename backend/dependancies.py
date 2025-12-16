""" 
Author: Matthieu Rouet
Date of creation: 02/12/2025

Documentation:
Utils functions to handle authentification and tokens
"""

# library imports
from fastapi import Depends, HTTPException, status
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
import sqlite3
from pydantic import BaseModel
from datetime import timedelta, timezone, datetime
import jwt

# module imports
from .db_webcafe import WebCafeDB

# Constants
ACCESS_TOKEN_EXPIRES_MINUTES = 30
ALGORITHM = "HS256"
SECRET_KEY = "060d236eebec58d5c66cbab9b9961a7d38414536b5d1c7e3d0286eaa25ff765e"


db = WebCafeDB()

oauth2scheme = OAuth2PasswordBearer(tokenUrl="token")   # url which it defaults to to lend JWT

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


def authenticate_user(username, pwd):
    hpwd = pwd_hash.hash(pwd)
    try:
        db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
        hpwd = db.userGetHashedPwd(username)
        db.conn.close()
        if hpwd != -2:
            return pwd_hash.verify(pwd, hpwd) 
    except:
        return False


# hashing password so that database loss would not result in plain passwords being exposed
def get_password_hash(plain_passwd):
    return pwd_hash.hash(plain_passwd)


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
    except jwt.ExpiredSignatureError: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="JWT has expired")
    except jwt.InvalidTokenError:
        raise credentials_exception
    return login

def elevated_rights(user):
    db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
    su_rights = db.check_superuser(user) 
    teacher_rights = db.check_teacher(user)
    db.conn.close()
    return (su_rights == 1) or (teacher_rights == 1)