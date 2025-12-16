""" 
Author: Matthieu Rouet
Date of creation: 02/12/2025

Documentation:
Test router file
"""

from fastapi import APIRouter

router = APIRouter(prefix="/status", tags=["status"])

@router.get("/healthcheck")
async def health_check():
    return {"status":"ok"}