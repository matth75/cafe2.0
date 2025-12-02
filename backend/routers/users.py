""" 
Author: Matthieu Rouet
Date of creation: 02/12/2025

Documentation:
User managment router. Handles user creation, modification, getting personnal infos.
If superuser, you can get a list of all users.
"""


# generic imports
from fastapi import Depends, HTTPException, status, APIRouter, Query
from typing import Annotated
import sqlite3
from pydantic import BaseModel, EmailStr, field_validator
from datetime import timedelta, timezone, datetime, date
import jwt
import re

# backend module imports
from ..db_webcafe import WebCafeDB
from ..dependancies import get_password_hash, get_current_user


router = APIRouter(prefix="/users", tags=["users"])

db = WebCafeDB()


# define a request model for sending data (POST)
class User(BaseModel):
    login: Annotated[str, Query(min_length=1, max_length=20)]
    email:Annotated[EmailStr, Query(max_length=50)]
    nom:Annotated[str, Query(max_length=30)]
    prenom:Annotated[str, Query(max_length=30)]
    hpwd:Annotated[str, Query(max_length=100)]  # password not actually hashed (hpwd), but name compatible with frontend
    birthday:Annotated[date, Query(default="2000-01-01")] 
    promo_id:str | None = ""
    teacher:bool | None = False
    superuser:bool | None = False
    noteKfet:Annotated[str, Query(default="NoteDefault", max_length=30)]
    
    
    @field_validator('*', mode='before')
    def sanitize_strings(cls, v):
        if isinstance(v, str):
            # Strip spaces
            v = v.strip()

            # Reject strings with SQL metacharacters
            if re.search(r"[;'\"\\]", v):
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid characters {v}")
        return v
    

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(user:User):
    """automaticaly parses User, if format ok, then adds user in db if possible"""
    # try 10 times with wait if SQL base already used ?
    db.conn = sqlite3.connect(db.dbname, check_same_thread=False)

    res = db.insertUser(login=user.login,
                        nom=user.nom,
                        prenom=user.prenom,
                        hpwd=get_password_hash(user.hpwd), 
                        email=user.email,
                        promo_str=user.promo_id,  # type: ignore
                        superuser=user.superuser,  # type: ignore
                        teacher=user.teacher,   # type: ignore
                        noteKfet=user.noteKfet,
                        birthday=user.birthday)     # type: ignore
    
    db.conn.close()
    if res == -1:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    if res == -2:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database unreacheable")
    return {"message":"User succesfully created", "login":str(user.login)}

@router.get("/me")
async def get_my_info(current_user_login : Annotated[str, Depends(get_current_user)]):
    db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
    user_info = db.get_user(current_user_login)
    db.conn.close()
    return user_info

@router.post("/modify")
async def modify_my_data(current_user_login : Annotated[str, Depends(get_current_user)], user_info:dict):
    db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
    res = db.user_modify(current_user_login, user_info)
    db.conn.close()
    if res == -1:
        return HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="empty data to update")
    if res == -2:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="unable to edit info")
    if res == -3:
        return HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="wrong fields provided")
    return HTTPException(status_code=status.HTTP_202_ACCEPTED, detail=f"user {current_user_login} succesfully modified")


@router.get("/all")
async def get_allUsers(current_user_login : Annotated[str, Depends(get_current_user)]):
    db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
    user_rights = db.check_superuser(current_user_login)    
    db.conn.close()
    if user_rights == 1:
        db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
        user_info = db.user_getall()
        db.conn.close()
        return user_info
    else:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"user {current_user_login} is not superuser")
    
