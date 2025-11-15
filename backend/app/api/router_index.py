from fastapi import APIRouter
from app.api import (
    router_code,
    router_leisure,
    router_station,
    router_observation,
    router_data,
)

router = APIRouter()
router.include_router(router_code.router)
router.include_router(router_leisure.router)
router.include_router(router_station.router)
router.include_router(router_observation.router)
router.include_router(router_data.router)
