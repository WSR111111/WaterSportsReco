from fastapi import APIRouter
from . import routes_region, routes_station, routes_observation, routes_sports, routes_leisure

api_router = APIRouter()
api_router.include_router(routes_region.router, prefix="/region")
api_router.include_router(routes_station.router, prefix="/station")
api_router.include_router(routes_observation.router, prefix="/observation")
api_router.include_router(routes_sports.router, prefix="/sports")
api_router.include_router(routes_leisure.router, prefix="/leisure")