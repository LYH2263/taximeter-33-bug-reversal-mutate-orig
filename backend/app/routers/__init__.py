from fastapi import APIRouter
from app.routers import dashboard, fare, history, reversal, settings, tariff, trips

api = APIRouter(prefix="/api")
for r in (dashboard, trips, tariff, fare, reversal, history, settings):
    api.include_router(r.router)
