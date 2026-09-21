from fastapi import APIRouter
from app.schemas.fare import CompareRequest, FareRequest
from app.services.taxi_service import TaxiService
router = APIRouter()
@router.post("/fare")
def post_fare(body: FareRequest):
    with TaxiService() as s:
        return s.fare(body.distance_km, body.slow_min, body.night, body.trip_id, body.persist)
@router.post("/compare")
def post_compare(body: CompareRequest):
    with TaxiService() as s:
        return s.compare(body.distance_km, body.slow_min, body.persist)
