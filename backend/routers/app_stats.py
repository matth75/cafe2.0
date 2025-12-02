from fastapi import APIRouter

router = APIRouter(prefix="/status", tags=["status"])

@router.get("/healthcheck")
async def health_check():
    return {"status":"ok"}