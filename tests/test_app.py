from fastapi.testclient import TestClient
from backend.server import app, create_access_token  
from backend.db_webcafe import WebCafeDB
import pytest
import sqlite3

client = TestClient(app)


def test_run_app():
    response = client.get("/")  # get root
    assert response is not None # test if app is running

    # test fetching database
    