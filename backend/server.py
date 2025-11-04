from typing import Annotated
from pydantic import BaseModel, field_validator, EmailStr
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import sqlite3
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import date, timedelta, timezone, datetime
from pwdlib import PasswordHash
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import re

# ------- JWT --------
ACCESS_TOKEN_EXPIRES_MINUTES = 30
ALGORITHM = "HS256"
SECRET_KEY = "060d236eebec58d5c66cbab9b9961a7d38414536b5d1c7e3d0286eaa25ff765e"

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
    from db_webcafe import WebCafeDB, dict_promos
else:
    from backend.db_webcafe import WebCafeDB


oauth2scheme = OAuth2PasswordBearer(tokenUrl="token")   # url which it defaults to to lend JWT

# create FastAPI app
app = FastAPI()


# enable CORS : 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


db = WebCafeDB()

# define a request model for sending data (POST)
class User(BaseModel):
    login: Annotated[str, Query(min_length=1, max_length=20)]
    email:Annotated[EmailStr, Query(max_length=50)]
    nom:Annotated[str, Query(max_length=30)]
    prenom:Annotated[str, Query(max_length=30)]
    hpwd:Annotated[str, Query(max_length=100)]
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
    

class UserPassword(BaseModel):
    login: Annotated[str, Query(min_length=1, max_length=20)]
    hpwd: Annotated[str, Query(max_length=100)]

class Event(BaseModel):
    pass

class Calendar(BaseModel):
    pass


@app.post("/users/create", status_code=status.HTTP_201_CREATED)
async def create_user(user:User):
    """automaticaly parses User, if format ok, then adds user in db if possible"""
    # try 10 times with wait if SQL base already used ?
    db.conn = sqlite3.connect(db.dbname, check_same_thread=False)

    res = db.insertUser(login=user.login,
                        nom=user.nom,
                        prenom=user.prenom,
                        hpwd=user.hpwd, 
                        email=user.email,
                        promo_str=user.promo_id, 
                        superuser=user.superuser,
                        teacher=user.teacher,
                        noteKfet=user.noteKfet,
                        birthday=user.birthday)
    
    db.conn.close()
    if res == -1:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    if res == -2:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database unreacheable")
    return {"message":"User succesfully created", "login":str(user.login)}

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
    except jwt.ExpiredSignatureError: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="JWT has expired")
    except jwt.InvalidTokenError:
        raise credentials_exception
    return login


dummyICS = ["icsM1", "icsM2"]
list_authorized_M1 = ["mylogin", "hello4"]


@app.post("/rights/set/teacher")
async def set_use_teacher(current_user_login : Annotated[str, Depends(get_current_user)], new_teacher_login:str):
    db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
    user_rights = db.check_superuser(current_user_login)    # seems ok
    db.conn.close()
    if user_rights == 1:    # user is superuser
        res = db.set_Teacher(new_teacher_login)
        return HTTPException(status_code=status.HTTP_200_OK, detail=f"User {new_teacher_login} succesfully updated rights to teacher")
    elif user_rights == -1:
        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED, detail=f"user {current_user_login} is not superuser")
    else:
        raise HTTPException (status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="could not reach database")


@app.get("/users/me")
async def get_my_info(current_user_login : Annotated[str, Depends(get_current_user)]):
    db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
    user_info = db.get_user(current_user_login)
    db.conn.close()
    return user_info

@app.post("/users/modify")
async def modify_my_data(current_user_login : Annotated[str, Depends(get_current_user)], user_info:dict):
    try :
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
    except:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.get("/ics/M2")
async def post_calendar(current_login : Annotated[str, Depends(get_current_user)]): 
    if (current_login in list_authorized_M1):
        return dummyICS[1]
    return "Access denied / not on the list"


@app.get("/calendars/available")
async def get_calendars():
    return list(dict_promos.keys())[1:]


@app.get("/users/all")
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
    
@app.get("/")
async def read_root():
    return {"message":"Welcome to the webcafe server"}

@app.get("/ics/testICS")
async def return_test_ics():
    return FileResponse("../ics/test.ics", filename="test.ics", media_type="text/ics")