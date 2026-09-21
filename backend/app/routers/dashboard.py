from fastapi import APIRouter
from app.services.taxi_service import TaxiService
router = APIRouter()
@router.get("/dashboard")
def dashboard():
    with TaxiService() as s: return s.dashboard()
