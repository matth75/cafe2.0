import requests


URL = "http://localhost:8000/create"

data = {
    "username":"John",
    "email":"oneemail@gmail.com",
    "hashed_pwd":"segxjhkqjeskrv"
    }

response = requests.post(URL, json=data)

print(response)