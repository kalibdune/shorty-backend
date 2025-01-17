from fastapi import APIRouter

from shorty.endpoints.url import router as url_router

routers = APIRouter(prefix="/api")

routers.include_router(url_router)
