from fastapi import APIRouter, HTTPException
from app.schemas.fare import ReverseRequest
from app.services.taxi_service import ReversalError, TaxiService
router = APIRouter()
@router.post("/runs/{run_id}/reverse")
def reverse_run(run_id: int, body: ReverseRequest):
    with TaxiService() as s:
        try:
            return s.reverse(run_id, body.distance_km, body.slow_min, body.preview)
        except ReversalError as e:
            raise HTTPException(e.status_code, e.detail)
