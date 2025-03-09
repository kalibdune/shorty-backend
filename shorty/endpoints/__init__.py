from fastapi import APIRouter

from shorty.endpoints.url import hash_router
from shorty.endpoints.url import router as url_router
from shorty.endpoints.user import router as user_router

routers = APIRouter()

api_routers = APIRouter(prefix="/api")
api_routers.include_router(url_router, tags=["Url"])
api_routers.include_router(user_router, tags=["User"])

routers.include_router(api_routers)
routers.include_router(hash_router, tags=["Hash"])
