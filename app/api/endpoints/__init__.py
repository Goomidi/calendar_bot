from fastapi import APIRouter

from app.api.endpoints.calendar import router as bot_router

router = APIRouter()

router.include_router(bot_router, prefix="/calendar", tags=["calendar"])
