from fastapi import APIRouter, HTTPException
from app.services.taxi_service import TaxiService
router = APIRouter()
@router.get("/trips")
def list_trips():
    with TaxiService() as s: return {"items": s.list_trips()}
@router.get("/trips/{trip_id}")
def get_trip(trip_id: int):
    with TaxiService() as s:
        row = s.trip(trip_id)
        if not row: raise HTTPException(404)
        return row
