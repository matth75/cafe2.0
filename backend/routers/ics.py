""" ICS management router """


# generic imports
from fastapi import Depends, HTTPException, status, APIRouter, Query, Request
from fastapi.responses import FileResponse
from typing import Annotated
from pydantic import BaseModel, field_validator
import sqlite3
from datetime import timezone, datetime
import json, os, fcntl, re


# backend module imports
from ..db_webcafe import WebCafeDB
from ..dependancies import get_password_hash, get_current_user


router = APIRouter(prefix="/ics", tags=["ics"])

# define path for csv and ics here
ICS_ROOT_PATH = "ics"
ICS_ALL = "all.ics"
DEFAULT_DATETIME = datetime(2012, 12, 21, 00, 32)  # fin du monde !

class Event(BaseModel):
    start: Annotated[datetime, Query(default=DEFAULT_DATETIME)] 
    end:  Annotated[datetime, Query(default=DEFAULT_DATETIME)]
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


db = WebCafeDB()

@router.get("/testICS")
async def return_test_ics():
    return FileResponse("../ics/test.ics", filename="test.ics", media_type="text/ics")


@router.get("/generated_test")
async def return_ics_generated():
    return FileResponse("../wow.ics", filename="wow.ics", media_type="text/ics")

@router.get("/get_all")
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
                

@router.post("/insert")
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

@router.get("/delete")
async def delete_event(uid_str:str):
    """ Deletes an event from database using its unique id"""
    db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
    uid = 0
    try:
        uid = int(uid_str.split('@')[0])
    except:
        return  HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="uid error")
    
    res = db.deleteEvent(uid)
    db.conn.close()
    if res == -1:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"event with unique id:{uid} not found")
    if res == -2:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="database error")
    if res == -3:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"event unique id:{id} <= 0. Not possible")
    return HTTPException(status_code=status.HTTP_200_OK, detail=f"event with unique id {id} succesfully deleted")


@router.get("/event_filter")
async def get_event_ids(event_criteria: Annotated[Event, Depends()]):
    """
    Asynchronously build a query from the provided Event criteria, fetch matching event IDs
    from the database, and return the full event details for those IDs.
    """

    db.conn = sqlite3.connect(db.dbname, check_same_thread=False)
    query_dict = {}
    # if criteria is provided, add it to the query dict
    if event_criteria.start != DEFAULT_DATETIME:
        query_dict["start"] = event_criteria.start
    if event_criteria.end != DEFAULT_DATETIME:
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
