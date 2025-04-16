from fastapi import APIRouter
from api.endpoints import story_writer

router = APIRouter()

router.include_router(
    story_writer.router,
    tags=["story-writer"]
)
