from typing import Annotated
from pydantic import BaseModel
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

oauth2scheme = OAuth2PasswordBearer(tokenUrl="token")


# create FastAPI app
app = FastAPI()

# define a request model for sending data (POST)
class Item(BaseModel):
    name: str
    price: float
    in_stock: bool

# GET endpoint (retrieve data)
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query": q}

# POST endpoint (send data)
@app.post("/items/")
def create_item(item: Item):
    return {"message": "Item received", "item": item}

