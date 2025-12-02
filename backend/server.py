from typing import Annotated
from pydantic import BaseModel, field_validator, EmailStr
from fastapi import FastAPI, Depends, HTTPException, Query, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import sqlite3
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import date, timedelta, timezone, datetime
from pwdlib import PasswordHash
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import re
import os
import fcntl
import json

DEVELOPPMENT_MODE = True

# ------- JWT --------
ACCESS_TOKEN_EXPIRES_MINUTES = 30
ALGORITHM = "HS256"
SECRET_KEY = "060d236eebec58d5c66cbab9b9961a7d38414536b5d1c7e3d0286eaa25ff765e"

# define path for csv and ics here
CSV_ROOT_PATH = "csv"
ICS_ROOT_PATH = "ics"
ICS_ALL = "all.ics"

pwd_hash = PasswordHash.recommended()

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
    from db_webcafe import WebCafeDB, load_inverse_promos
else:
    from backend.db_webcafe import WebCafeDB


oauth2scheme = OAuth2PasswordBearer(tokenUrl="token")   # url which it defaults to to lend JWT

# create FastAPI app
if DEVELOPPMENT_MODE:
    app = FastAPI(root_path="/api")

else:
    app = FastAPI(
        docs_url=None,       # disables Swagger UI (/docs)
        redoc_url=None,      # disables ReDoc (/redoc)
        openapi_url=None     # disables OpenAPI JSON schema (/openapi.json)
    )


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
    

class UserPassword(BaseModel):
    login: Annotated[str, Query(min_length=1, max_length=20)]
    hpwd: Annotated[str, Query(max_length=100)]


default_datetime = datetime(2012, 12, 21, 00, 32)  # fin du monde !

class Event(BaseModel):
    start: Annotated[datetime, Query(default=default_datetime)] 
    end:  Annotated[datetime, Query(default=default_datetime)]
    matiere: Annotated[str, Query(max_length=20, default="")] 
    type_cours: Annotated[str, Query(max_length=20, default="")] 
    infos_sup: Annotated[str, Query(max_length=50, default="")]
    classroom_id: int | None = 0
    user_id: int | None = 0
    promo_id: int | None = 0

    @field_validator('*', mode='before')
    def sanitize_strings(cls, v):
        # reuse same sanitization rules as User: strip and reject SQL metachars
        if isinstance(v, str):
            v = v.strip()
            if re.search(r"[;'\"\\]", v):
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid characters {v}")
        return v
    
class NewEvent(BaseModel):
    start: datetime 
    end:  datetime
    matiere: Annotated[str, Query(min_length=2, max_length=20)] 
    type_cours: Annotated[str, Query(min_length=2, max_length=20)] 
    infos_sup: Annotated[str, Query(min_length=2, max_length=50, default="")]
    classroom_str: str
    user_id: int | None = 0
    promo_id: int | None = 0

    @field_validator('*', mode='before')
    def sanitize_strings(cls, v):
        # reuse same sanitization rules as User: strip and reject SQL metachars
        if isinstance(v, str):
            v = v.strip()
            if re.search(r"[;'\"\\]", v):
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid characters {v}")
        return v


# hashing password so that database loss would not result in plain passwords being exposed
def get_password_hash(plain_passwd):
    return pwd_hash.hash(plain_passwd)


@app.post("/users/create", status_code=status.HTTP_201_CREATED)
async def create_user(user:User):
    """automaticaly parses User, if format ok, then adds user in db if possible"""
    # try 10 times with wait if SQL base already used ?
    db.conn = sqlite3.connect(db.dbname, check_same_thread=False)

    res = db.insertUser(login=user.login,
                        nom=user.nom,
                        prenom=user.prenom,
                        hpwd=pwd_hash.hash(user.hpwd), 
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

# @app.post("/users/login")
# async def check_user(u_pwd:UserPassword):
#     try:
#         db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
#         res = db.userCheckPassword(u_pwd.login, u_pwd.hpwd)
#         db.conn.close()
#         if res == -1 or res == -2:  
#             raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#         # if res == -2:
#         #     return "user does not exist"
#         else:
#             access_token = create_access_token(data={"sub":u_pwd.login})
#         return Token(access_token=access_token, token_type='bearer') 
#     except:
#         return "could not acces database"


# ------- ICS management -------
# class JsonCalendar():
#     pass

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
        hpwd = db.userGetHashedPwd(username)
        print(hpwd)
        db.conn.close()
        if hpwd != -2:
            return pwd_hash.verify(pwd, hpwd) 
    except:
        return False


@app.post("/token")
async def login(form_data:Annotated[OAuth2PasswordRequestForm, Depends()]):
    # login = form_data.username
    # hpwd = form_data.password
    try:
        auth_bool = authenticate_user(form_data.username, form_data.password)
    except:
        "db innaccessible"
    if not auth_bool:  
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
        db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
        res = db.set_Teacher(new_teacher_login)
        db.conn.close()
        if res == 1:
            return HTTPException(status_code=status.HTTP_200_OK, detail=f"User {new_teacher_login} succesfully updated rights to teacher")
        else:
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"could not modify user {new_teacher_login}")
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


@app.get("/ics/M2")
async def post_calendar(current_login : Annotated[str, Depends(get_current_user)]): 
    if (current_login in list_authorized_M1):
        return dummyICS[1]
    return "Access denied / not on the list"


@app.get("clasrrom/modify")

@app.get("/classrooms/all")
async def get_classrooms():
    try:
        conn = sqlite3.connect(db.dbname, check_same_thread=False)
        rows = conn.execute("SELECT location FROM classroom").fetchall()
        return [r[0] for r in rows]
    except:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@app.get("/classrooms/all/detail")
async def get_classrooms_detail():
    try:
        conn = sqlite3.connect(db.dbname, check_same_thread=False)
        table_info = conn.execute("PRAGMA table_info(classroom)").fetchall()
        column_names = [t[1] for t in table_info]
        print(column_names)
        res = {}
        rows = conn.execute("SELECT * FROM classroom").fetchall()
        for r in rows:
            res[r[0]] = dict(zip(column_names[1:], r[1:]))
        return res
    except:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@app.get("/calendars/available")
async def get_calendars():
    return list(load_inverse_promos())


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


@app.get("/ics/generated_test")
async def return_ics_generated():
    return FileResponse("../wow.ics", filename="wow.ics", media_type="text/ics")

@app.get("/ics/get_all")
async def return_all_events():
    ics_name = ICS_ALL
    meta_sidecar = f"{ICS_ROOT_PATH}/{ICS_ALL}.meta"
    # check if version has changed, i.e. modifications inside SQL db
    db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
    c = db.conn.cursor()
    try:
        row = c.execute("SELECT version FROM meta WHERE key='events'").fetchone()
        db_version = row[0] if row else 0
    finally:
        c.close()
        db.conn.close()

    cached_version = None
    if os.path.exists(meta_sidecar):
        with open(meta_sidecar, 'r') as mf:
            obj = json.load(mf)
            cached_version = obj.get("version")

    # ics full path
    ics_path = f"{ICS_ROOT_PATH}/{ics_name}"

    # check if file doesnt exists or as been modifed
    if not os.path.exists(ics_path) or cached_version != db_version:
        lock_path = ics_path + ".lock"  # avoid race conditions while accessing the file
        with open(lock_path, "w") as lockf:
            try:
                fcntl.flock(lockf, fcntl.LOCK_EX)
                res = db.generate_ics(db.dbname, ics_path)
                if res == -2:
                    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="could not query database")
                if res == -1:
                    return HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail="no events found for the given filters")
                if res == -3:
                    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="could not save ics.file")
                with open(meta_sidecar, "w") as mf:
                    json.dump({"version": db_version, "generated_at": datetime.utcnow().isoformat()}, mf)
            finally:
                fcntl.flock(lockf, fcntl.LOCK_UN)

    return FileResponse(ics_path, filename=ics_name, media_type="text/ics")
                


@app.get("/healthcheck")
async def health_check():
    return {"status":"ok"}


@app.get("/version")
async def get_version():
    return {"version":"1.0.0"}

@app.get("/test/event_filter")
async def get_event_ids(event_criteria: Annotated[Event, Depends()]):
    """
    Asynchronously build a query from the provided Event criteria, fetch matching event IDs
    from the database, and return the full event details for those IDs.
    Behaviour
    - Opens a SQLite connection and assigns it to db.conn.
    - Constructs a query_dict containing only the criteria that differ from their default
        values:
            - start, end: compared against `default_datetime`
            - matiere, type_cours, infos_sup: included if non-empty strings
            - classroom_id, user_id, promo_id: included if not None and > 0
    - Prints the constructed query_dict (side effect).
    - Calls db._get_events_id(query_dict) to obtain a sequence of matching event IDs.
        - If db._get_events_id returns -1, returns an HTTPException with status 500.
        - Otherwise, calls db._get_events_on_ids(ids) to retrieve full event details.
    - Closes the database connection before returning.
    Args:
            event_criteria (Event, provided via Depends()):
                    An Event-like object used as a filter. Only fields that are set to values
                    different from their defaults are used to build the query:
                    - start, end (datetime-like): compared to `default_datetime`.
                    - matiere, type_cours, infos_sup (str): included when not empty.
                    - classroom_id, user_id, promo_id (int or None): included when not None and > 0.
    Returns:
            On success: the value returned by db._get_events_on_ids(ids) (presumably a list
            or iterable of event detail objects/dicts).
            On database query failure: an instance of fastapi.HTTPException with
            status_code=500 and detail="query failed".
    Side effects:
            - Opens a SQLite connection with sqlite3.connect(db.dbname, check_same_thread=False)
                and assigns it to db.conn.
            - Prints the constructed query dictionary to stdout.
            - Closes db.conn before returning.
            - Calls two db helper functions: db._get_events_id and db._get_events_on_ids.
    Notes:
            - The function currently returns an HTTPException instance on error rather than
                raising it; callers (e.g., FastAPI) should handle that pattern appropriately.
            - The function relies on module-level symbols: db, default_datetime, sqlite3,
                and status; ensure these are available in the module's scope.
    """

    db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
    query_dict = {}
    # if criteria is provided, add it to the query dict
    if event_criteria.start != default_datetime:
        query_dict["start"] = event_criteria.start
    if event_criteria.end != default_datetime:
        query_dict["end"] = event_criteria.end
    if event_criteria.matiere != "":
        query_dict["matiere"] = event_criteria.matiere
    if event_criteria.type_cours != "":
        query_dict["type_cours"] = event_criteria.type_cours
    if event_criteria.infos_sup != "":
        query_dict["infos_sup"] = event_criteria.infos_sup
    if event_criteria.classroom_id is not None and event_criteria.classroom_id > 0:
        query_dict["classroom_id"] = event_criteria.classroom_id    
    if event_criteria.user_id is not None and event_criteria.user_id > 0:
        query_dict["user_id"] = event_criteria.user_id
    if event_criteria.promo_id is not None and event_criteria.promo_id > 0:
        query_dict["promo_id"] = event_criteria.promo_id


    # print(query_dict), for debugging only
        
    ids = db._get_events_id(query_dict) # query database for events
    
    if ids == -1:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="query failed")
    else:
            res = db._get_events_on_ids(ids)    # returns events detail for all events  
    db.conn.close()
    return res


@app.post("/ics/insert")
async def insert_event(e: Annotated[NewEvent, Depends()]):
    """ Adds an event to database. """
    db.conn = sqlite3.connect(db.dbname, check_same_thread=False)

    classroom_id = db.get_classroom_id(e.classroom_str)
    if classroom_id < 0:
        return HTTPException(status_code=status.HTTP_418_IM_A_TEAPOT, detail=f"no classroom in database by the name {e.classroom_str}")
    # convert classroom to id
    res = db.insertEvent(start=e.start,
                         end =e.end,
                         matiere=e.matiere,
                         type_cours=e.type_cours,
                         infos_sup=e.infos_sup,
                         classroom_id=classroom_id,   #type: ignore
                         user_id=e.user_id, #type: ignore
                         promo_id=e.promo_id    #type: ignore
                         )
    db.conn.close()
    if res == -1:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"event starting at {e.start} for promotion {e.promo_id} already exists")
    if res == -2:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="database error")
    
    return HTTPException(status_code=status.HTTP_200_OK, detail=f"event succesfully added")

@app.get("/ics/delete")
async def delete_event(uid:int):
    """ Deletes an event from database using its unique id"""
    db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
    res = db.deleteEvent(uid)
    db.conn.close()
    if res == -1:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"event with unique id:{uid} not found")
    if res == -2:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="database error")
    if res == -3:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"event unique id:{id} <= 0. Not possible")
    return HTTPException(status_code=status.HTTP_200_OK, detail=f"event with unique id {id} succesfully deleted")


@app.get("/csv")
async def get_csv_by_promo(promo_str:str):
    # remove whitespaces and replace them with underscores for file creation
    promo_str_path= promo_str
    promo_str_path = "_".join(promo_str_path.split())

    # validate promo_str contains only alphanumeric chars
    if not re.fullmatch(r'[A-Za-z0-9_]+', promo_str_path):
        return HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Invalid promotion name: {promo_str}")

    db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
    # get promo id
    promo_id = db.get_promo_id(promo_str)
    if promo_id < 0:
        return HTTPException(status_code=status.HTTP_418_IM_A_TEAPOT, detail=f"no promotion in database by the name {promo_str}")
    

    if not os.path.isdir(CSV_ROOT_PATH):  # folder does not exist
        try:
            os.mkdir(CSV_ROOT_PATH)
        except:
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"error while managing folders")

    # full path         
    csv_path = f"{CSV_ROOT_PATH}/{promo_str_path}.csv"

    res = db.generate_csv(promo_id, csv_path)
    db.conn.close()
    if res == -2:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="database error")
    
    return FileResponse(csv_path, filename=f"{promo_str_path}.csv", media_type="text/ics")

# Create url endpoints for each promotion in SQL table promos. 
# Functions test if a modification was made to the SQL table "events" by compararing the version stored in
# "all.ics.meta" file and the version number in the "meta" SQL table. If they are different, or the ics file we are supposed
# to generate is missing from filesystem, the function then (re)generates the ics file. 
# The async endpoint then returns the file if everything worked correctly and throws errors if something went wrong.

def create_dynamic_ics_endpoint(promo_id, promo_name: str):
    async def endpoint(request: Request):
        """ Endpoint for downloading ics"""
        ics_name = f"dynamic_{promo_name}.ics"
        meta_sidecar = f"{ICS_ROOT_PATH}/all.ics.meta"
        # check if version has changed, i.e. modifications inside SQL db
        db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
        try:
            row = db.conn.execute("SELECT version FROM meta WHERE key='events'").fetchone()
            db_version = row[0] if row else 0
        finally:
            db.conn.close()

        cached_version = None
        if os.path.exists(meta_sidecar):
            with open(meta_sidecar, 'r') as mf:
                obj = json.load(mf)
                cached_version = obj.get("version")

        if not os.path.isdir(ICS_ROOT_PATH):
            try:
                os.mkdir(ICS_ROOT_PATH)
            except:
                return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"error while managing folders")

        # full path
        ics_path = f"{ICS_ROOT_PATH}/{ics_name}"

        # check if file doesnt exists or as been modifed
        if not os.path.exists(ics_path) or cached_version != db_version:
            lock_path = ics_path + ".lock"  # avoid race conditions while accessing the file
            with open(lock_path, "w") as lockf:
                try:
                    fcntl.flock(lockf, fcntl.LOCK_EX)
                    res = db.generate_ics(db.dbname, ics_path, promo_id=promo_id)
                    if res == -2:
                        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="could not query database")
                    if res == -1:
                        return HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail="no events found for the given filters")
                    if res == -3:
                        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="could not save ics.file")
                    with open(meta_sidecar, "w") as mf:
                        json.dump({"version": db_version, "generated_at": str(datetime.now(timezone.utc))}, mf)
                finally:
                    fcntl.flock(lockf, fcntl.LOCK_UN)
        return FileResponse(ics_path, filename=f"{promo_name}.ics", media_type="text/ics", status_code=status.HTTP_200_OK)
    return endpoint

def find_allpromos():
    db.conn = sqlite3.connect(db.dbname)
    calendars = db.conn.execute("SELECT promo_id, promo_name FROM promo").fetchall()
    calendars_underscores = []

    for c in calendars:
        calendars_underscores.append([c[0], "_".join(c[1].split())])

    for c in calendars_underscores:
        app.add_api_route(f"/ics/{c[1]}", create_dynamic_ics_endpoint(c[0], c[1]), methods=["GET"])

find_allpromos()


# @app.get("/xls/by_promo")
# async def get_xls_by_promo()