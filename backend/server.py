from typing import Annotated
from pydantic import BaseModel, field_validator, EmailStr
from fastapi import FastAPI, Depends, Query
from fastapi.security import OAuth2PasswordBearer
import sqlite3

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
    
class Event(BaseModel):
    pass

class Calendar(BaseModel):
    pass


@app.post("/users/create")
async def create_user(user:User):
    # automaticaly parses User, if format ok, then check if User in database
    #TODO: add user in database
    db.conn = sqlite3.connect(db.dbname)
    res = db.insertUser(user.login, user.nom, user.prenom, user.hpwd, user.email,
                   superuser=user.superuser, owner=user.owner, noteKfet=user.noteKfet)
    db.conn.close()
    return res

@app.get("/")
async def read_root():
    return {"message":"Hello, World!"}
