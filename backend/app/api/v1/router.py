from fastapi import APIRouter

from app.api.v1 import auth, subjects, topics

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(subjects.router)
api_router.include_router(topics.router)
