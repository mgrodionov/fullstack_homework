from fastapi import APIRouter

from app.api.user import router as user_route

router = APIRouter()

router.include_router(user_route, prefix="", tags=["user"])
