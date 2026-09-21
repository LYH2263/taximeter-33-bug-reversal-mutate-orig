from fastapi import APIRouter
from app.services.taxi_service import TaxiService
router = APIRouter()
@router.get("/settings")
def settings():
    with TaxiService() as s: return s.settings()
