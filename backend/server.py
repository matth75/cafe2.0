""" 
Author: Matthieu Rouet
Date of creation: 09/10/2025

Documentation:
Main file. The FastAPI app is created here. Some endpoints are needed in this file, and some are here as default location?
All other endpoints are imported here as routers objects, from the routers folder. They are sorted according to their purposes :
 - /users  : user management (login, modification, personnal infos...) ;
 - /ics    : handling ics files (download, adding/removing events) ;
 - /status : test router.   

Dependancies for the app (raw functions, not endpoints) are stored in the dependancies.py file.
"""

# library imports
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, Query, status, Request
import sqlite3
from datetime import timezone, datetime
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import re
import os
import fcntl
import json

# module imports
from .routers import app_stats, users, ics
from .dependancies import *
from .db_webcafe import WebCafeDB, load_inverse_promos

# Constants
CSV_ROOT_PATH = "csv"


# ---------------------- #

# create FastAPI app
# DEVELOPPMENT_MODE = True
# if DEVELOPPMENT_MODE:
#     app = FastAPI(root_path="/api")
#     app.include_router(app_stats.router)

# else:
#     app = FastAPI(
#         docs_url=None,       # disables Swagger UI (/docs)
#         redoc_url=None,      # disables ReDoc (/redoc)
#         openapi_url=None     # disables OpenAPI JSON schema (/openapi.json)
#     )


# Create FastAPI app here
app = FastAPI(root_path="/api")
app.include_router(app_stats.router)
app.include_router(users.router)
app.include_router(ics.router)

# enable CORS : idk what it does but its necessary, ask someone else !
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],   # weird config but works somehow
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebCafeDB object to handle interactions with database
db = WebCafeDB()

# generic endpoints
@app.get("/")
async def read_root():
    find_allpromos()    # create new urls if necessary
    return {"message":"Welcome to the webcafe server"}

@app.get("/version")
async def get_version():
    return {"version":"1.0.0"}


# ---- token endpoint, to manage Json Web Tokens (JWT) ---- #

class UserPassword(BaseModel):
    login: Annotated[str, Query(min_length=1, max_length=20)]
    hpwd: Annotated[str, Query(max_length=100)]

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
    
# --------------------------------------------------------- #


# get the list of all classrooms
@app.get("/classrooms/all")
async def get_classrooms():
    try:
        conn = sqlite3.connect(db.dbname, check_same_thread=False)
        rows = conn.execute("SELECT location FROM classroom").fetchall()
        return [r[0] for r in rows]
    except:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# get a detailled list of all classrooms
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

# get the list of available calendars
@app.get("/calendars/available")
async def get_calendars():
    return list(load_inverse_promos())


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

# NB : PAS RÉUSSI À METTRE ÇA DANS ICS.PY, OUPSI

def create_dynamic_ics_endpoint(promo_id, promo_name: str):
    async def endpoint(request: Request):
        """ Endpoint for downloading ics"""
        ics_name = f"dynamic_{promo_name}.ics"
        meta_sidecar = f"{ics.ICS_ROOT_PATH}/all.ics.meta"
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

        if not os.path.isdir(ics.ICS_ROOT_PATH):
            try:
                os.mkdir(ics.ICS_ROOT_PATH)
            except:
                return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"error while managing folders")

        # full path
        ics_path = f"{ics.ICS_ROOT_PATH}/{ics_name}"

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
        app.add_api_route(f"/ics/{c[1]}", create_dynamic_ics_endpoint(c[0], c[1]), methods=["GET"], tags=["ics"])


find_allpromos()
