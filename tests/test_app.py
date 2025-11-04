import sys
from pathlib import Path

# ajoute la racine du projet au sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from backend.server import app
from backend.db_webcafe import WebCafeDB
import pytest
import sqlite3

client = TestClient(app)


def test_run_app():
    response = client.get("/")  # get root
    assert response is not None # test if app is running

    # test fetching database
    