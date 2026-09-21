from fastapi import APIRouter
from app.services.taxi_service import TaxiService
router = APIRouter()
@router.get("/tariff")
def get_tariff():
    with TaxiService() as s: return s.tariff()
