from typing import Annotated
from pydantic import BaseModel, field_validator, EmailStr
from fastapi import FastAPI, Depends, Query
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

oauth2scheme = OAuth2PasswordBearer(tokenUrl="token")

# create FastAPI app
app = FastAPI()

# define a request model for sending data (POST)
class User(BaseModel):
    username: Annotated[str, Query(min_length=4, max_length=10)]
    email:EmailStr 
    hashed_pwd : Annotated[str, Query(min_length=4)]
    
class Event(BaseModel):
    pass

class Calendar(BaseModel):
    pass


@app.post("/create")
async def create_user(user:User):
    # automaticaly parses User, if format ok, then check if User in database
    #TODO: add user in database
    return 0

@app.get("/")
async def read_root():
    return {"message":"Hello, World!"}
